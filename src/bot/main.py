import asyncio
import sys

from aiogram import Bot, Dispatcher
from loguru import logger

from src.bot.config import settings
from src.bot.handlers import router
from src.bot.scheduler import init_scheduler, stop_scheduler
from src.database.session import run_migrations


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
    dp.include_router(router)

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
