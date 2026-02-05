from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from apscheduler import AsyncScheduler
from apscheduler.triggers.date import DateTrigger
from loguru import logger

if TYPE_CHECKING:
    from aiogram import Bot

from src.bot.i18n import get_text
from src.database import crud
from src.database.session import async_session

WALK_TIMEOUT_MINUTES = 5

# Store job IDs by user_id for cancellation
_pending_jobs: dict[int, str] = {}
_scheduler: AsyncScheduler | None = None
_bot: "Bot | None" = None


async def init_scheduler(bot: "Bot") -> AsyncScheduler:
    """Initialize the scheduler."""
    global _scheduler, _bot
    _bot = bot
    _scheduler = AsyncScheduler()
    await _scheduler.__aenter__()
    await _scheduler.start_in_background()
    logger.debug("Scheduler started in background")
    return _scheduler


async def stop_scheduler() -> None:
    """Stop the scheduler."""
    global _scheduler
    if _scheduler:
        await _scheduler.__aexit__(None, None, None)
        _scheduler = None
        logger.debug("Scheduler stopped")


async def schedule_walk_finalization(user_id: int, walk_id: int) -> None:
    """Schedule auto-finalization of a walk after timeout."""
    global _scheduler, _pending_jobs

    if _scheduler is None:
        logger.warning("Scheduler not initialized, cannot schedule walk finalization")
        return

    # Cancel existing job for this user if any
    await cancel_walk_timer(user_id)

    run_time = datetime.now() + timedelta(minutes=WALK_TIMEOUT_MINUTES)
    job_id = await _scheduler.add_schedule(
        _auto_finalize_walk,
        trigger=DateTrigger(run_time=run_time),
        args=[user_id, walk_id],
        id=f"walk_{user_id}_{walk_id}",
    )
    _pending_jobs[user_id] = job_id
    logger.debug(f"Scheduled auto-finalization for walk {walk_id} at {run_time}")


async def cancel_walk_timer(user_id: int) -> None:
    """Cancel pending walk timer for a user."""
    global _scheduler, _pending_jobs

    if _scheduler is None:
        return

    job_id = _pending_jobs.pop(user_id, None)
    if job_id:
        try:
            await _scheduler.remove_schedule(job_id)
            logger.debug(f"Cancelled walk timer for user {user_id}")
        except Exception as e:
            logger.debug(f"Could not cancel timer for user {user_id}: {e}")


async def _auto_finalize_walk(user_id: int, walk_id: int) -> None:
    """Auto-finalize walk and broadcast (called by scheduler)."""
    global _bot, _pending_jobs

    _pending_jobs.pop(user_id, None)
    logger.info(f"Auto-finalizing walk {walk_id} for user {user_id}")

    if _bot is None:
        logger.error("Bot not available for auto-finalization")
        return

    async with async_session() as session:
        walk = await crud.finalize_walk(session, walk_id)
        if walk is None:
            logger.warning(f"Walk {walk_id} not found for auto-finalization")
            return

        user = await crud.get_user_by_telegram_id(session, walk.user.telegram_id)
        if user is None:
            logger.warning(f"User not found for walk {walk_id}")
            return

        # Send confirmation to walker
        await _bot.send_message(
            chat_id=user.telegram_id,
            text=get_text("walk_sent", user.language),
        )

        # Import here to avoid circular import
        from src.bot.keyboards import main_keyboard

        await _bot.send_message(
            chat_id=user.telegram_id,
            text=get_text("walk_button", user.language),
            reply_markup=main_keyboard(user.language),
        )

        # Broadcast to all users
        await _broadcast_walk(session, walk, user)


async def _broadcast_walk(session, walk, walker_user) -> None:
    """Broadcast walk notification to all active users."""
    global _bot

    if _bot is None:
        logger.error("Bot not available for broadcast")
        return

    all_users = await crud.get_all_active_users(session)
    logger.info(f"Broadcasting walk {walk.id} to {len(all_users)} users")

    for user in all_users:
        # Build message in user's language
        username = walker_user.username or f"User {walker_user.telegram_id}"
        time_str = walk.walked_at.strftime("%H:%M")

        message = get_text("walk_logged", user.language).format(
            username=username, time=time_str
        )

        # Add parameters if any
        params = []
        if walk.didnt_poop:
            params.append(get_text("param_didnt_poop", user.language))
        if walk.long_walk:
            params.append(get_text("param_long_walk", user.language))

        if params:
            message += "\n" + get_text("additional", user.language).format(
                params=", ".join(params)
            )

        try:
            await _bot.send_message(chat_id=user.telegram_id, text=message)
            logger.debug(f"Sent walk notification to user {user.telegram_id}")
        except Exception as e:
            logger.warning(f"Failed to send notification to user {user.telegram_id}: {e}")
