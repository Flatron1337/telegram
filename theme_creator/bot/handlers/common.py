from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

common_router = Router(name="common")


@common_router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Send welcome introduction and usage instructions."""
    text = (
        "👋 <b>Привет! Я генератор тем для Telegram.</b>\n\n"
        "Отправь мне <b>любое фото или картинку</b> (как фото или файл без сжатия), и я:\n"
        "1. Проанализирую цветовую гамму алгоритмом кластеризации.\n"
        "2. Подберу гармоничные акценты, фон и пузыри с высокой читаемостью (WCAG 2.1).\n"
        "3. Создам темы для <b>Telegram Desktop (.tdesktop-theme)</b>, <b>Android (.attheme)</b> "
        "и <b>iOS (.tgios-theme)</b>.\n"
        "4. Позволю переключать режим: полная тема с обоями или лёгкая (~15 КБ).\n\n"
        "🎨 <i>Готовые пресеты: /presets</i>\n"
        "✨ <i>Интерактивный Web App редактор с прозрачностью: /studio</i>\n"
        "📸 <i>Или просто отправь изображение в чат!</i>"
    )
    await message.answer(text)


@common_router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Provide detailed installation instructions for Desktop, Android, and iOS."""
    text = (
        "📖 <b>Как пользоваться ботом и устанавливать темы:</b>\n\n"
        "🎨 <b>Команды:</b>\n"
        "• /studio — визуальный Web App редактор с настройкой прозрачности\n"
        "• /presets — готовые дизайнерские пресеты (Cyberpunk Rem, Ram, AMOLED и др.)\n"
        "• /help — эта справка\n\n"
        "💻 <b>Telegram Desktop (Windows / macOS / Linux):</b>\n"
        "1. Скачай файл с расширением <code>.tdesktop-theme</code>.\n"
        "2. Нажми на него прямо в Telegram или перетащи файл в окно программы.\n"
        "3. В появившемся окне нажми <b>«Применить тему»</b>.\n\n"
        "📱 <b>Telegram Android:</b>\n"
        "1. Скачай файл с расширением <code>.attheme</code>.\n"
        "2. Нажми на файл в чате.\n"
        "3. Нажми кнопку <b>«Применить тему»</b> внизу экрана.\n\n"
        "🍎 <b>Telegram iOS (iPhone / iPad):</b>\n"
        "1. Скачай файл с расширением <code>.tgios-theme</code>.\n"
        "2. Нажми на файл в чате.\n"
        "3. В окне предпросмотра нажми кнопку <b>«Применить тему»</b>.\n\n"
        "💡 <i>Совет: В меню темы можно отключить встроенные обои, "
        "нажав «Обои в теме: Выкл», чтобы сохранить свои собственные обои чата.</i>"
    )

    await message.answer(text)



