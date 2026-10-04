from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.config import get_settings
from bot.handlers import common_router, theme_router
from bot.server import start_web_server


async def setup_commands(bot: Bot) -> None:
    """Register bot slash commands visible in Telegram UI menu."""
    commands = [
        BotCommand(command="start", description="Запустить бота и инструкцию"),
        BotCommand(command="studio", description="Theme Studio (Web App редактор)"),
        BotCommand(command="presets", description="Готовые дизайнерские пресеты"),
        BotCommand(command="help", description="Справка по установке тем"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    """Initialize dependencies and start Telegram polling loop."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger("theme_bot")

    settings = get_settings()
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp["settings"] = settings

    dp.include_router(common_router)
    dp.include_router(theme_router)

    await setup_commands(bot)
    web_runner = await start_web_server(
        host=settings.webapp_host,
        port=settings.webapp_port,
        bot=bot,
        bot_token=settings.bot_token.get_secret_value(),
    )

    logger.info("Bot successfully started in polling mode...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        if web_runner is not None:
            await web_runner.cleanup()
        await bot.session.close()



if __name__ == "__main__":
    asyncio.run(main())
