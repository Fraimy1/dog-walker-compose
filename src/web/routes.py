import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, unquote

from fastapi import APIRouter, Header, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from src.web.config import settings
from src.web.database import async_session
from src.web.queries import (
    get_all_users,
    get_hourly_distribution,
    get_leaderboard,
    get_long_walk_stats,
    get_poop_stats,
    get_walks_per_day,
    get_weekly_trends,
)

templates = Jinja2Templates(directory="src/web/templates")
router = APIRouter()


def verify_telegram_init_data(init_data: str, bot_token: str) -> dict | None:
    """Verify Telegram WebApp initData and return parsed data if valid.

    Returns the parsed user dict on success, None on failure.
    """
    parsed = parse_qs(init_data, keep_blank_values=True)
    received_hash = parsed.pop("hash", [None])[0]
    if not received_hash:
        return None

    # Build data-check-string: sorted key=value pairs joined by newlines
    # Each value in parse_qs is a list, take the first element
    data_pairs = sorted(
        (k, v[0]) for k, v in parsed.items()
    )
    data_check_string = "\n".join(f"{k}={v}" for k, v in data_pairs)

    # HMAC chain: secret_key = HMAC-SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    # Extract user info
    user_raw = parsed.get("user", [None])[0]
    if not user_raw:
        return None

    try:
        return json.loads(unquote(user_raw))
    except (json.JSONDecodeError, TypeError):
        return None


def check_access(init_data: str | None) -> JSONResponse | None:
    """Verify initData and check allowed_users. Returns error response or None if OK."""
    # No initData = regular browser access, allow it
    if not init_data:
        return None

    # initData present = Telegram Mini App, verify it
    if not settings.bot_token:
        return None

    user = verify_telegram_init_data(init_data, settings.bot_token)
    if user is None:
        return JSONResponse({"error": "Invalid credentials"}, status_code=403)

    if settings.allowed_users and user.get("id") not in settings.allowed_users:
        return JSONResponse({"error": "Access denied"}, status_code=403)

    return None


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Page HTML loads without auth — the JS SDK provides initData client-side,
    # which is then sent as a header on all API calls for verification.
    async with async_session() as session:
        users = await get_all_users(session)
    return templates.TemplateResponse("dashboard.html", {"request": request, "users": users})


@router.get("/api/dashboard")
async def dashboard_api(
    start: str | None = Query(None),
    end: str | None = Query(None),
    user_id: int | None = Query(None),
    x_telegram_init_data: str | None = Header(None),
):
    error = check_access(x_telegram_init_data)
    if error:
        return error

    today = datetime.now(timezone.utc).date()
    if start:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
    else:
        start_dt = datetime.combine(today - timedelta(days=13), datetime.min.time())
    if end:
        end_dt = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    else:
        end_dt = datetime.combine(today, datetime.max.time())

    async with async_session() as session:
        return {
            "leaderboard": await get_leaderboard(session, start_dt, end_dt, user_id),
            "walks_per_day": await get_walks_per_day(session, start_dt, end_dt, user_id),
            "weekly_trends": await get_weekly_trends(session, start_dt, end_dt, user_id),
            "poop_stats": await get_poop_stats(session, start_dt, end_dt, user_id),
            "long_walk_stats": await get_long_walk_stats(session, start_dt, end_dt, user_id),
            "hourly_distribution": await get_hourly_distribution(session, start_dt, end_dt, user_id),
        }
