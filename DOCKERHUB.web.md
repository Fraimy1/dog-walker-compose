# Dog Walker — Web Dashboard

Statistics dashboard for the [dog-walker-bot](https://hub.docker.com/r/blaze698/dog-walker-bot). Displays walk history, leaderboards, hourly distributions, and poop/long-walk stats with dark/light theme support.

Built with FastAPI + Uvicorn. Multi-stage image (~150 MB), runs as non-root user.

## Quick start

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=mysql+aiomysql://user:pass@host:3306/dbname \
  blaze698/dog-walker-web
```

Dashboard available at `http://localhost:8000`.

## Environment variables

| Variable        | Required | Description                                |
| --------------- | -------- | ------------------------------------------ |
| `DATABASE_URL`  | Yes      | MySQL connection string                    |
| `BOT_TOKEN`     | No       | Telegram bot token — enables Mini App auth |
| `ALLOWED_USERS` | No       | Comma-separated Telegram IDs to whitelist  |

## Docker Compose

See the full multi-service setup (bot + web + MySQL) at the [GitHub repository](https://github.com/Fraimy1/dog-walker-compose).
