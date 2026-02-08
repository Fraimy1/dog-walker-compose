from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _user_filter(user_id: int | None) -> str:
    if user_id is not None:
        return " AND w.user_id = :user_id"
    return ""


def _params(start_dt: datetime, end_dt: datetime, user_id: int | None) -> dict:
    p = {"start": start_dt, "end": end_dt}
    if user_id is not None:
        p["user_id"] = user_id
    return p


async def get_leaderboard(
    session: AsyncSession, start_dt: datetime, end_dt: datetime, user_id: int | None = None
) -> list[dict]:
    sql = text(
        "SELECT COALESCE(u.display_name, u.username, CONCAT('User ', u.telegram_id)) AS name, "
        "COUNT(*) AS walk_count "
        "FROM walks w JOIN users u ON w.user_id = u.id "
        "WHERE w.is_finalized = 1 AND w.walked_at BETWEEN :start AND :end"
        + _user_filter(user_id)
        + " GROUP BY w.user_id ORDER BY walk_count DESC"
    )
    result = await session.execute(sql, _params(start_dt, end_dt, user_id))
    return [{"name": r.name, "walk_count": r.walk_count} for r in result]


async def get_walks_per_day(
    session: AsyncSession, start_dt: datetime, end_dt: datetime, user_id: int | None = None
) -> list[dict]:
    sql = text(
        "SELECT DATE(w.walked_at) AS day, COUNT(*) AS count "
        "FROM walks w "
        "WHERE w.is_finalized = 1 AND w.walked_at BETWEEN :start AND :end"
        + _user_filter(user_id)
        + " GROUP BY DATE(w.walked_at) ORDER BY day"
    )
    result = await session.execute(sql, _params(start_dt, end_dt, user_id))
    return [{"day": str(r.day), "count": r.count} for r in result]


async def get_weekly_trends(
    session: AsyncSession, start_dt: datetime, end_dt: datetime, user_id: int | None = None
) -> list[dict]:
    sql = text(
        "SELECT DATE(w.walked_at - INTERVAL WEEKDAY(w.walked_at) DAY) AS week_start, "
        "COUNT(*) AS count "
        "FROM walks w "
        "WHERE w.is_finalized = 1 AND w.walked_at BETWEEN :start AND :end"
        + _user_filter(user_id)
        + " GROUP BY week_start ORDER BY week_start"
    )
    result = await session.execute(sql, _params(start_dt, end_dt, user_id))
    return [{"week_start": str(r.week_start), "count": r.count} for r in result]


async def get_poop_stats(
    session: AsyncSession, start_dt: datetime, end_dt: datetime, user_id: int | None = None
) -> list[dict]:
    sql = text(
        "SELECT COALESCE(u.display_name, u.username, CONCAT('User ', u.telegram_id)) AS name, "
        "COUNT(*) AS total, SUM(w.didnt_poop) AS didnt_poop_count "
        "FROM walks w JOIN users u ON w.user_id = u.id "
        "WHERE w.is_finalized = 1 AND w.walked_at BETWEEN :start AND :end"
        + _user_filter(user_id)
        + " GROUP BY w.user_id ORDER BY total DESC"
    )
    result = await session.execute(sql, _params(start_dt, end_dt, user_id))
    return [
        {"name": r.name, "total": r.total, "didnt_poop_count": int(r.didnt_poop_count or 0)}
        for r in result
    ]


async def get_long_walk_stats(
    session: AsyncSession, start_dt: datetime, end_dt: datetime, user_id: int | None = None
) -> list[dict]:
    sql = text(
        "SELECT COALESCE(u.display_name, u.username, CONCAT('User ', u.telegram_id)) AS name, "
        "COUNT(*) AS total, SUM(w.long_walk) AS long_walk_count "
        "FROM walks w JOIN users u ON w.user_id = u.id "
        "WHERE w.is_finalized = 1 AND w.walked_at BETWEEN :start AND :end"
        + _user_filter(user_id)
        + " GROUP BY w.user_id ORDER BY total DESC"
    )
    result = await session.execute(sql, _params(start_dt, end_dt, user_id))
    return [
        {"name": r.name, "total": r.total, "long_walk_count": int(r.long_walk_count or 0)}
        for r in result
    ]


async def get_hourly_distribution(
    session: AsyncSession, start_dt: datetime, end_dt: datetime, user_id: int | None = None
) -> list[dict]:
    sql = text(
        "SELECT HOUR(w.walked_at) AS hour, COUNT(*) AS count "
        "FROM walks w "
        "WHERE w.is_finalized = 1 AND w.walked_at BETWEEN :start AND :end"
        + _user_filter(user_id)
        + " GROUP BY HOUR(w.walked_at) ORDER BY hour"
    )
    result = await session.execute(sql, _params(start_dt, end_dt, user_id))
    return [{"hour": r.hour, "count": r.count} for r in result]


async def get_all_users(session: AsyncSession) -> list[dict]:
    sql = text(
        "SELECT id, COALESCE(display_name, username, CONCAT('User ', telegram_id)) AS name "
        "FROM users WHERE is_active = 1 ORDER BY name"
    )
    result = await session.execute(sql)
    return [{"id": r.id, "name": r.name} for r in result]
