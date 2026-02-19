from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import Bot
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.config import settings
from src.bot.i18n import get_text
from src.database import crud


async def broadcast_walk(session: AsyncSession, walk, walker_user, bot: Bot) -> None:
    """Broadcast walk notification to all active users.

    Separated from scheduler to avoid circular imports and keep
    notification logic independent of scheduling concerns.
    """
    all_users = await crud.get_all_active_users(session)
    logger.info(f"Broadcasting walk {walk.id} to {len(all_users)} users")

    username = walker_user.display_name or walker_user.username or f"User {walker_user.telegram_id}"
    tz = ZoneInfo(settings.display_timezone)
    now = datetime.now(timezone.utc).astimezone(tz)
    time_now = now.strftime("%H:%M")
    time_walked = walk.walked_at.replace(tzinfo=timezone.utc).astimezone(tz).strftime("%H:%M")

    for user in all_users:
        message = get_text("walk_logged", user.language).format(
            username=username, time=time_now, time_walked=time_walked
        )

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
            await bot.send_message(chat_id=user.telegram_id, text=message)
            logger.debug(f"Sent walk notification to user {user.telegram_id}")
        except Exception as e:
            logger.warning(f"Failed to send notification to user {user.telegram_id}: {e}")
