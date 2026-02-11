import asyncio
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo
from loguru import logger

from src.bot.config import settings
from src.bot.handlers import router
from src.bot.middleware import WhitelistMiddleware
from src.bot.scheduler import init_scheduler, stop_scheduler
from src.database.session import run_migrations

TUNNEL_URL_FILE = Path("/shared/tunnel_url")


def setup_logging() -> None:
    """Configure loguru for console and file output."""
    # Remove default handler
    logger.remove()

    # Console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    # File handler with rotation
    logger.add(
        "data/bot.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )


async def get_webapp_url() -> str:
    """Get webapp URL from config or shared tunnel file."""
    if settings.webapp_url:
        return settings.webapp_url

    # /shared only exists inside Docker with the tunnel-data volume
    if not TUNNEL_URL_FILE.parent.exists():
        return ""

    logger.info("Waiting for tunnel URL...")
    for _ in range(30):
        if TUNNEL_URL_FILE.exists():
            url = TUNNEL_URL_FILE.read_text().strip()
            if url:
                return url
        await asyncio.sleep(1)

    logger.warning("Tunnel URL not found after 30s")
    return ""


async def main() -> None:
    """Main entry point."""
    setup_logging()
    logger.info("Starting bot...")

    # Run pending database migrations
    run_migrations()
    logger.info("Database migrated")

    # Create bot and dispatcher
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.update.outer_middleware(WhitelistMiddleware())
    dp.include_router(router)

    # Resolve webapp URL (from env or tunnel shared file)
    webapp_url = await get_webapp_url()
    if webapp_url:
        settings.webapp_url = webapp_url
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Statistics",
                web_app=WebAppInfo(url=webapp_url),
            )
        )
        logger.info(f"Menu button set to {webapp_url}")

    # Initialize scheduler
    await init_scheduler(bot)
    logger.info("Scheduler initialized")

    try:
        # Start polling
        logger.info("Bot is running...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Bot stopped with error: {e}")
    finally:
        logger.info("Shutting down...")
        await stop_scheduler()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
