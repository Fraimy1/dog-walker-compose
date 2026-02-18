# Docker Compose Improvements — Explained

A breakdown of the changes made to bring this project up to production standards, with examples and reasoning for each.

---

## 1. Multi-stage Dockerfile

**Before:**
```dockerfile
FROM python:3.12-slim
RUN pip install -r requirements-web.txt
COPY src/ src/
CMD ["uvicorn", ...]
```

**After:**
```dockerfile
FROM python:3.12-slim AS builder      # Stage 1
RUN pip install -r requirements-web.txt

FROM python:3.12-slim AS production   # Stage 2
COPY --from=builder /opt/venv /opt/venv
USER appuser
CMD ["uvicorn", ...]
```

**Why it matters:**

When pip installs packages, it downloads compilers, headers, and build tools — stuff that's only needed to *build* the package, not to *run* it. In a single-stage build all that junk stays in your image forever.

With multi-stage, Stage 1 does all the dirty work. Stage 2 starts fresh and copies *only the finished result* — the virtual environment with compiled packages. The build tools never make it into the final image.

This shrinks image size significantly (a typical Python app goes from ~600 MB to ~150 MB) and reduces the attack surface — fewer tools in the image means fewer things an attacker could exploit if they got in.

---

## 2. Non-privileged User

**Before:** container ran as `root` (Docker default)

**After:**
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

**Why it matters:**

By default Docker containers run as root. If your app has a vulnerability (e.g. a path traversal bug) and an attacker gains code execution, they'd be root *inside* the container. Depending on your setup, that can mean reading secrets, accessing mounted volumes, or even breaking out to the host.

Running as a regular user means an attacker gets far less power. It's the principle of **least privilege** — the app only has exactly the permissions it needs to serve web requests, nothing more.

---

## 3. MySQL Healthcheck

**Before:** MySQL started, and Docker immediately told bot/web "dependency is ready" — even though MySQL takes ~10–30 seconds to actually initialize.

**After:**
```yaml
mysql:
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
    interval: 10s
    retries: 5
    start_period: 30s
```

```yaml
bot:
  depends_on:
    mysql:
      condition: service_healthy   # waits for the healthcheck to pass
```

**Why it matters:**

Without a healthcheck, `depends_on` only waits for the container to *start*, not for MySQL to be *ready to accept connections*. The bot would crash immediately trying to connect to a database that was still initializing. You'd see errors like `Can't connect to MySQL server`.

The healthcheck runs `mysqladmin ping` every 10 seconds. Only when that returns OK does Docker consider MySQL "healthy" and allow dependent services to start. `start_period: 30s` gives MySQL a grace period before failed checks count against it.

---

## 4. Explicit Networks

**Before:** All 3 services shared one auto-created default network — everything could talk to everything.

**After:**
```yaml
networks:
  backend:   # internal — bot, web, mysql
  frontend:  # external-facing — web only

mysql:
  networks:
    - backend   # mysql is ONLY on backend — not reachable from frontend
```

**Why it matters:**

In the real world you don't want your database reachable from the same network segment as your public-facing services. If your web app is compromised, the attacker should have to break through another layer to reach the DB.

Here `mysql` is isolated to `backend` only. The `web` service bridges both networks — it needs to talk to MySQL *and* be reachable from outside. This mirrors how production architectures work — a **DMZ pattern**:

```
Internet → frontend network → web service → backend network → mysql
                                  ↑
                                 bot
```

---

## 5. Docker Compose Profiles

**Before:** All services always started together, including optional tools.

**After:**
```yaml
adminer:
  profiles:
    - dev    # only starts when you explicitly request the dev profile
```

```bash
# Production — only bot, web, mysql
docker compose up -d

# Development — adds Adminer DB UI on port 8080
docker compose --profile dev up -d
```

**Why it matters:**

Adminer is a dev tool — you'd never want a database management UI exposed in production. Profiles let you define groups of services that only run in specific contexts.

This is the same idea as having separate `requirements-dev.txt` and `requirements.txt` — you don't ship debug tools to prod.

---

## Summary

| Change | Core principle |
|---|---|
| Multi-stage build | Don't ship build tools to production |
| Non-root user | Least privilege |
| Healthcheck + `depends_on` condition | Don't start dependents until the dependency is actually ready |
| Explicit networks | Isolate services that don't need to talk to each other |
| Profiles | Separate dev tooling from production services |

These are all standard practices you'd see in any production Docker setup. The lab is essentially teaching you the gap between "it works on my machine" and "it's safe and reliable in production."
