from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from bot.services.presets import THEME_PRESETS


def create_theme_selection_keyboard(
    session_id: str,
    with_wallpaper: bool = True,
) -> InlineKeyboardMarkup:
    """Build interactive action buttons for downloading theme files and toggling wallpaper mode."""
    wp_label = "🖼 Обои в теме: Вкл ✅" if with_wallpaper else "🖼 Обои в теме: Выкл ❌ (Лёгкая)"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Скачать всё (Desktop + Android + iOS)",
                    callback_data=f"dl:all:{session_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💻 TDesktop (Тёмная)",
                    callback_data=f"dl:td_dark:{session_id}",
                ),
                InlineKeyboardButton(
                    text="💻 TDesktop (Светлая)",
                    callback_data=f"dl:td_light:{session_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📱 Android (Тёмная)",
                    callback_data=f"dl:an_dark:{session_id}",
                ),
                InlineKeyboardButton(
                    text="📱 Android (Светлая)",
                    callback_data=f"dl:an_light:{session_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🍎 iOS (Тёмная)",
                    callback_data=f"dl:ios_dark:{session_id}",
                ),
                InlineKeyboardButton(
                    text="🍎 iOS (Светлая)",
                    callback_data=f"dl:ios_light:{session_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=wp_label,
                    callback_data=f"wp:toggle:{session_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌓 Превью (Тёмная / Светлая)",
                    callback_data=f"pv:toggle:{session_id}",
                ),
                InlineKeyboardButton(
                    text="🎨 Пресеты",
                    callback_data="preset:menu",
                ),
            ],
        ]
    )


def create_presets_keyboard() -> InlineKeyboardMarkup:
    """Build interactive menu with available curated style presets."""
    buttons: list[list[InlineKeyboardButton]] = []
    for preset_id, preset in THEME_PRESETS.items():
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{preset.emoji} {preset.title}",
                    callback_data=f"preset:apply:{preset_id}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_webapp_reply_keyboard(webapp_url: str) -> ReplyKeyboardMarkup:
    """Build persistent menu button that launches the Telegram Mini App."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🎨 Открыть Theme Studio",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        ],
        resize_keyboard=True,
    )


def create_webapp_inline_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    """Build inline button to launch Theme Studio Mini App directly from messages."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Открыть Theme Studio (Mini App)",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        ]
    )

