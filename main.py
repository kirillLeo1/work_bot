from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Settings
from bot.db import create_tables, setup_database
from bot.handlers.admin import router as admin_router
from bot.handlers.common import router as common_router
from bot.handlers.worker import router as worker_router
from bot.middlewares import SettingsMiddleware


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = Settings.from_env()
    setup_database(settings.database_url)
    await create_tables()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    middleware = SettingsMiddleware(settings)
    dp.message.middleware(middleware)
    dp.callback_query.middleware(middleware)

    dp.include_router(common_router)
    dp.include_router(worker_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
