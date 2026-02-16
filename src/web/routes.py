from datetime import datetime, timedelta

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    async with async_session() as session:
        users = await get_all_users(session)
    return templates.TemplateResponse("dashboard.html", {"request": request, "users": users})


@router.get("/api/dashboard")
async def dashboard_api(
    start: str | None = Query(None),
    end: str | None = Query(None),
    user_id: int | None = Query(None),
):
    today = datetime.now().date()
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
