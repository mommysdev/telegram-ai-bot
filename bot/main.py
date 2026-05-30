"""Main entry point for the Telegram AI bot."""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from .config import config
from .handlers import router
from .storage import init_db


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def main():
    """Start the bot."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Initializing database...")
    await init_db()

    logger.info(f"Starting bot with {config.ai_backend} backend...")
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
