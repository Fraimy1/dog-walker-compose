from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Walk


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None = None
) -> User:
    """Get existing user or create a new one."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def set_user_language(session: AsyncSession, user_id: int, language: str) -> None:
    """Set user's preferred language."""
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        user.language = language
        await session.commit()


async def set_display_name(session: AsyncSession, user_id: int, display_name: str) -> None:
    """Set user's broadcast display name."""
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        user.display_name = display_name
        await session.commit()


async def get_user_by_telegram_id(
    session: AsyncSession, telegram_id: int
) -> User | None:
    """Get user by Telegram ID."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_walk(session: AsyncSession, user_id: int) -> Walk:
    """Create a new walk record."""
    walk = Walk(user_id=user_id)
    session.add(walk)
    await session.commit()
    await session.refresh(walk)
    return walk


async def get_pending_walk(session: AsyncSession, user_id: int) -> Walk | None:
    """Get user's pending (not finalized) walk."""
    stmt = select(Walk).where(Walk.user_id == user_id, Walk.is_finalized == False)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_walk_params(
    session: AsyncSession,
    walk_id: int,
    didnt_poop: bool | None = None,
    long_walk: bool | None = None,
) -> None:
    """Update walk parameters."""
    stmt = select(Walk).where(Walk.id == walk_id)
    result = await session.execute(stmt)
    walk = result.scalar_one_or_none()

    if walk:
        if didnt_poop is not None:
            walk.didnt_poop = didnt_poop
        if long_walk is not None:
            walk.long_walk = long_walk
        await session.commit()


async def update_walk_time(session: AsyncSession, walk_id: int, walked_at: datetime) -> None:
    """Set custom walked_at timestamp."""
    stmt = select(Walk).where(Walk.id == walk_id)
    result = await session.execute(stmt)
    walk = result.scalar_one_or_none()

    if walk:
        walk.walked_at = walked_at
        await session.commit()


async def finalize_walk(session: AsyncSession, walk_id: int) -> Walk | None:
    """Mark walk as finalized."""
    stmt = select(Walk).where(Walk.id == walk_id)
    result = await session.execute(stmt)
    walk = result.scalar_one_or_none()

    if walk:
        walk.is_finalized = True
        await session.commit()
        await session.refresh(walk)

    return walk


async def delete_walk(session: AsyncSession, walk_id: int) -> None:
    """Delete a walk record."""
    stmt = select(Walk).where(Walk.id == walk_id)
    result = await session.execute(stmt)
    walk = result.scalar_one_or_none()

    if walk:
        await session.delete(walk)
        await session.commit()


async def get_all_active_users(session: AsyncSession) -> list[User]:
    """Get all active users for broadcast."""
    stmt = select(User).where(User.is_active == True)
    result = await session.execute(stmt)
    return list(result.scalars().all())
