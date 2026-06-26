import os
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReactionTypeEmoji
from aiogram.filters import CommandStart

from dotenv import load_dotenv
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import web

# Загружаем переменные окружения из файла .env (для локального запуска)
load_dotenv()

# Получаем токен и ID из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_USER_ID = int(os.getenv("MY_USER_ID", 0))

# Настройка прокси для бесплатных аккаунтов PythonAnywhere
session = None
if os.environ.get("PYTHONANYWHERE_SITE"):
    session = AiohttpSession(proxy="http://proxy.server:3128")

bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот, который ставит дизлайки (👎) на все сообщения, кроме сообщений моего создателя.")

@dp.message()
async def react_to_message(message: types.Message):
    # Проверяем, не от тебя ли это сообщение
    if message.from_user and message.from_user.id != MY_USER_ID:
        try:
            # Выбираем случайную реакцию
            emoji_to_set = random.choice(["👎", "❤️‍🔥"])
            # Ставим выбранную реакцию
            await message.react([ReactionTypeEmoji(type="emoji", emoji=emoji_to_set)])
        except Exception as e:
            if "MESSAGE_ID_INVALID" in str(e):
                pass # Это сервисное сообщение (например, "Пользователь зашел в группу"), на него нельзя поставить реакцию
            else:
                logging.error(f"Не удалось поставить реакцию: {e}")

# Функции для фейкового веб-сервера
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Фейковый веб-сервер запущен на порту {port} (для обмана Render)")

async def main():
    logging.basicConfig(level=logging.INFO)
    # Удаляем старые накопившиеся сообщения, чтобы бот не тормозил при запуске
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем наш фейковый сервер
    await start_dummy_server()
    
    # Запуск бота
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
