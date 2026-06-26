import os
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReactionTypeEmoji
from aiogram.filters import CommandStart

from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (для локального запуска)
load_dotenv()

# Получаем токен и ID из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_USER_ID = int(os.getenv("MY_USER_ID", 0))

bot = Bot(token=BOT_TOKEN)
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

async def main():
    logging.basicConfig(level=logging.INFO)
    # Удаляем старые накопившиеся сообщения, чтобы бот не тормозил при запуске
    await bot.delete_webhook(drop_pending_updates=True)
    # Запуск бота
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
