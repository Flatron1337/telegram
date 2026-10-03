from __future__ import annotations

import io
import json
from typing import TYPE_CHECKING

from aiogram import Bot, F, Router
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto, Message

from bot.config import Settings
from bot.keyboards.theme_keyboards import (
    create_presets_keyboard,
    create_theme_selection_keyboard,
    create_webapp_inline_keyboard,
)
from bot.services.presets import THEME_PRESETS
from bot.services.session_store import ThemeSessionStore
from bot.services.theme_service import ProcessedThemeResult, ThemeService

if TYPE_CHECKING:
    from aiogram.types import Document, PhotoSize

theme_router = Router(name="theme")
theme_service = ThemeService()
session_store = ThemeSessionStore()


def _is_image_document(doc: Document) -> bool:
    mime = doc.mime_type or ""
    name = (doc.file_name or "").lower()
    return mime.startswith("image/") or name.endswith((".jpg", ".jpeg", ".png", ".webp"))


async def _download_telegram_file(bot: Bot, file_id: str) -> bytes:
    buffer = io.BytesIO()
    await bot.download(file_id, destination=buffer)
    return buffer.getvalue()


@theme_router.message(F.photo)
async def handle_photo(message: Message, bot: Bot, settings: Settings) -> None:
    """Process compressed photo sent by user."""
    photos: list[PhotoSize] = message.photo or []
    if not photos:
        return

    best_photo = photos[-1]
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if best_photo.file_size and best_photo.file_size > max_bytes:
        await message.answer(f"⚠️ Размер файла превышает лимит {settings.max_file_size_mb} МБ.")
        return

    await _process_and_reply(message, bot, best_photo.file_id)


@theme_router.message(F.document)
async def handle_document(message: Message, bot: Bot, settings: Settings) -> None:
    """Process uncompressed image file sent as document."""
    doc = message.document
    if not doc or not _is_image_document(doc):
        return

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if doc.file_size and doc.file_size > max_bytes:
        await message.answer(f"⚠️ Размер файла превышает лимит {settings.max_file_size_mb} МБ.")
        return

    await _process_and_reply(message, bot, doc.file_id)


@theme_router.message(F.text == "/presets")
async def handle_presets_command(message: Message) -> None:
    """Display curated theme presets."""
    caption = (
        "🎨 <b>Готовые дизайнерские пресеты</b>\n\n"
        "Выберите один из авторских стилей, адаптированных под Telegram Desktop и Android:"
    )
    await message.answer(caption, reply_markup=create_presets_keyboard())


@theme_router.message(F.text.in_({"/studio", "/app"}))
async def handle_studio_command(message: Message, settings: Settings) -> None:
    """Provide launch button for Telegram Theme Studio Mini App with transparency."""
    if settings.webapp_url:
        caption = (
            "✨ <b>Telegram Theme Studio (Mini App)</b>\n\n"
            "Интерактивный визуальный редактор тем прямо в Telegram:\n"
            "• 🎨 Выбор любых цветов палитры в реальном времени\n"
            "• 🫧 <b>Поддержка прозрачности пузырей сообщений</b>\n"
            "• 📱 Живой симулятор чата с мгновенным обновлением\n"
            "• 🚀 Экспорт для Desktop, Android и iOS одним кликом!"
        )
        kb = create_webapp_inline_keyboard(settings.webapp_url)
        await message.answer(caption, reply_markup=kb)
    else:
        text = (
            "✨ <b>Telegram Theme Studio (Mini App)</b>\n\n"
            "Веб-приложение Theme Studio запущено локально на порту <code>8080</code>.\n"
            "Чтобы открыть его внутри Telegram, укажите <code>WEBAPP_URL</code> в файле "
            "<code>.env</code> (например, через <code>npx cloudflared tunnel "
            "--url http://localhost:8080</code>)."
        )
        await message.answer(text)



@theme_router.message(F.web_app_data)
async def handle_webapp_data(message: Message) -> None:
    """Process custom theme payload received from Telegram Theme Studio Mini App."""
    raw = message.web_app_data.data if message.web_app_data else "{}"
    status = await message.answer("⏳ <i>Генерирую кастомную тему из Theme Studio...</i>")

    try:
        payload = json.loads(raw)
        result = await theme_service.process_custom_palette_async(payload)
        session_id = session_store.create(result)

        has_trans = bool(
            payload.get("has_transparency")
            or payload.get("in_bubble_alpha", 255) < 255
            or payload.get("out_bubble_alpha", 255) < 255
        )
        trans_line = "🫧 <b>Прозрачность:</b> Включена ✅\n" if has_trans else ""

        caption = (
            "✨ <b>Кастомная тема из Theme Studio готова!</b>\n\n"
            f"🎨 <b>Название:</b> {payload.get('name', 'Custom Studio Theme')}\n"
            f"🎯 <b>Акцент:</b> <code>{result.dark_theme.accent.hex.upper()}</code>\n"
            f"🌙 <b>Фон:</b> <code>{result.dark_theme.background.hex.upper()}</code>\n"
            f"{trans_line}\n"
            "Выберите тему для загрузки:"
        )

        preview_file = BufferedInputFile(
            result.dark_preview_png, filename="preview_studio.png"
        )
        await message.answer_photo(
            photo=preview_file,
            caption=caption,
            reply_markup=create_theme_selection_keyboard(
                session_id, with_wallpaper=False
            ),
        )
    except Exception as exc:
        await message.answer("❌ Произошла ошибка при сборке темы из Theme Studio.")
        raise exc
    finally:
        await status.delete()



async def _process_and_reply(message: Message, bot: Bot, file_id: str) -> None:
    status_msg = await message.answer("⏳ <i>Анализирую изображение и генерирую темы...</i>")

    try:
        raw_bytes = await _download_telegram_file(bot, file_id)
        result = await theme_service.process_image_async(raw_bytes)
        session_id = session_store.create(result)

        caption = (
            "✨ <b>Темы успешно созданы!</b>\n\n"
            f"🎯 <b>Акцент:</b> <code>{result.dark_theme.accent.hex.upper()}</code>\n"
            f"🌙 <b>Фон тёмной:</b> <code>{result.dark_theme.background.hex.upper()}</code>\n"
            f"☀️ <b>Фон светлой:</b> <code>{result.light_theme.background.hex.upper()}</code>\n\n"
            "Выберите тему для загрузки или скачайте всё одним кликом:"
        )

        preview_file = BufferedInputFile(result.dark_preview_png, filename="preview_dark.png")
        await message.answer_photo(
            photo=preview_file,
            caption=caption,
            reply_markup=create_theme_selection_keyboard(session_id, with_wallpaper=True),
        )
    except Exception as exc:
        await message.answer(
            "❌ Произошла ошибка при обработке изображения. Убедитесь, что это корректная картинка."
        )
        raise exc
    finally:
        await status_msg.delete()


def _collect_theme_files(
    res: ProcessedThemeResult,
    with_wallpaper: bool,
) -> dict[str, tuple[bytes, str, str]]:
    """Build mapping of action key to (payload, filename, caption)."""
    wp_suffix = "" if with_wallpaper else " (без обоев, лёгкая)"
    td_dark = (
        res.tdesktop_dark
        if with_wallpaper
        else (res.tdesktop_dark_pure or res.tdesktop_dark)
    )
    td_light = (
        res.tdesktop_light
        if with_wallpaper
        else (res.tdesktop_light_pure or res.tdesktop_light)
    )
    an_dark = (
        res.android_dark
        if with_wallpaper
        else (res.android_dark_pure or res.android_dark)
    )
    an_light = (
        res.android_light
        if with_wallpaper
        else (res.android_light_pure or res.android_light)
    )

    return {
        "td_dark": (
            td_dark,
            "theme_dark.tdesktop-theme",
            f"💻 Telegram Desktop (Тёмная тема{wp_suffix})",
        ),
        "td_light": (
            td_light,
            "theme_light.tdesktop-theme",
            f"💻 Telegram Desktop (Светлая тема{wp_suffix})",
        ),
        "an_dark": (
            an_dark,
            "theme_dark.attheme",
            f"📱 Telegram Android (Тёмная тема{wp_suffix})",
        ),
        "an_light": (
            an_light,
            "theme_light.attheme",
            f"📱 Telegram Android (Светлая тема{wp_suffix})",
        ),
        "ios_dark": (
            res.ios_dark,
            "theme_dark.tgios-theme",
            "🍎 Telegram iOS (Тёмная тема)",
        ),
        "ios_light": (
            res.ios_light,
            "theme_light.tgios-theme",
            "🍎 Telegram iOS (Светлая тема)",
        ),
    }


@theme_router.callback_query(F.data.startswith("dl:"))
async def handle_download_callback(callback: CallbackQuery, bot: Bot) -> None:
    """Handle theme file download requests."""
    data = callback.data or ""
    parts = data.split(":")
    if len(parts) != 3:
        await callback.answer("Некорректный запрос.", show_alert=True)
        return

    _, action, session_id = parts
    session = session_store.get(session_id)
    if session is None or callback.message is None:
        await callback.answer(
            "Срок действия сессии истёк. Отправьте картинку заново.", show_alert=True
        )
        return

    await callback.answer("Отправляю файлы тем...")
    chat_id = callback.message.chat.id
    files_map = _collect_theme_files(session.result, session.with_wallpaper)

    if action == "all":
        for content, filename, caption in files_map.values():
            await _send_single_theme(bot, chat_id, content, filename, caption)
    elif action in files_map:
        content, filename, caption = files_map[action]
        await _send_single_theme(bot, chat_id, content, filename, caption)


async def _send_single_theme(
    bot: Bot, chat_id: int, content: bytes, filename: str, caption: str
) -> None:
    file = BufferedInputFile(content, filename=filename)
    await bot.send_document(chat_id=chat_id, document=file, caption=caption)



@theme_router.callback_query(F.data.startswith("wp:toggle:"))
async def handle_wallpaper_toggle(callback: CallbackQuery) -> None:
    """Toggle wallpaper mode between embedded wallpaper and lightweight theme."""
    data = callback.data or ""
    session_id = data.split(":")[-1]
    session = session_store.get(session_id)
    if session is None or callback.message is None:
        await callback.answer("Сессия истекла.", show_alert=True)
        return

    session.with_wallpaper = not session.with_wallpaper
    await callback.message.edit_reply_markup(
        reply_markup=create_theme_selection_keyboard(
            session_id, with_wallpaper=session.with_wallpaper
        ),
    )
    status_text = (
        "Включены (полный размер)"
        if session.with_wallpaper
        else "Выключены (лёгкая тема ~15 КБ)"
    )
    await callback.answer(f"Обои: {status_text}")


@theme_router.callback_query(F.data == "preset:menu")
async def handle_presets_menu_callback(callback: CallbackQuery) -> None:
    """Show presets selection menu."""
    if callback.message is None:
        return
    caption = "🎨 <b>Готовые дизайнерские пресеты</b>\n\nВыберите стиль оформления:"
    await callback.message.answer(caption, reply_markup=create_presets_keyboard())
    await callback.answer()


@theme_router.callback_query(F.data.startswith("preset:apply:"))
async def handle_preset_apply_callback(callback: CallbackQuery) -> None:
    """Generate themes from selected preset and present preview & download buttons."""
    if callback.message is None:
        return

    preset_id = (callback.data or "").split(":")[-1]
    preset = THEME_PRESETS.get(preset_id)
    if preset is None:
        await callback.answer("Пресет не найден.", show_alert=True)
        return

    await callback.answer(f"Применяю пресет {preset.title}...")
    result = await theme_service.process_preset_async(preset_id)
    session_id = session_store.create(result)
    session = session_store.get(session_id)
    if session is not None:
        session.with_wallpaper = False

    caption = (
        f"{preset.emoji} <b>Пресет «{preset.title}» готов!</b>\n\n"
        f"📝 <i>{preset.description}</i>\n\n"
        f"🎯 <b>Акцент:</b> <code>{result.dark_theme.accent.hex.upper()}</code>\n"
        f"🌙 <b>Фон тёмной:</b> <code>{result.dark_theme.background.hex.upper()}</code>\n"
        f"☀️ <b>Фон светлой:</b> <code>{result.light_theme.background.hex.upper()}</code>\n\n"
        "Выберите тему для загрузки или скачайте всё одним кликом:"
    )
    preview_file = BufferedInputFile(result.dark_preview_png, filename=f"preview_{preset_id}.png")
    await callback.message.answer_photo(
        photo=preview_file,
        caption=caption,
        reply_markup=create_theme_selection_keyboard(session_id, with_wallpaper=False),
    )


@theme_router.callback_query(F.data.startswith("pv:toggle:"))
async def handle_preview_toggle(callback: CallbackQuery) -> None:
    """Switch preview card between dark and light themes."""
    data = callback.data or ""
    session_id = data.split(":")[-1]
    session = session_store.get(session_id)
    if session is None or callback.message is None:
        await callback.answer("Сессия истекла.", show_alert=True)
        return

    new_mode = "light" if session.current_preview == "dark" else "dark"
    session.current_preview = new_mode

    preview_bytes = (
        session.result.light_preview_png if new_mode == "light" else session.result.dark_preview_png
    )
    media = InputMediaPhoto(
        media=BufferedInputFile(preview_bytes, filename=f"preview_{new_mode}.png"),
        caption=callback.message.caption,
    )
    await callback.message.edit_media(
        media=media,
        reply_markup=create_theme_selection_keyboard(
            session_id, with_wallpaper=session.with_wallpaper
        ),
    )
    await callback.answer(f"Превью: {'Светлая' if new_mode == 'light' else 'Тёмная'} тема")
