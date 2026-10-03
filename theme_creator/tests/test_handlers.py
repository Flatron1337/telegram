from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

from bot.handlers.common import handle_help, handle_start
from bot.keyboards.theme_keyboards import create_theme_selection_keyboard


def test_theme_selection_keyboard_structure() -> None:
    kb_with_wp = create_theme_selection_keyboard("session_123", with_wallpaper=True)
    assert len(kb_with_wp.inline_keyboard) == 6

    all_callbacks = [
        btn.callback_data for row in kb_with_wp.inline_keyboard for btn in row if btn.callback_data
    ]
    assert "dl:all:session_123" in all_callbacks
    assert "dl:ios_dark:session_123" in all_callbacks
    assert "dl:ios_light:session_123" in all_callbacks
    assert "wp:toggle:session_123" in all_callbacks
    assert "pv:toggle:session_123" in all_callbacks
    assert "preset:menu" in all_callbacks

    # Verify toggle text
    wp_btn = [
        btn
        for row in kb_with_wp.inline_keyboard
        for btn in row
        if btn.callback_data == "wp:toggle:session_123"
    ][0]
    assert "Вкл ✅" in wp_btn.text

    kb_no_wp = create_theme_selection_keyboard("session_123", with_wallpaper=False)
    wp_btn_no = [
        btn
        for row in kb_no_wp.inline_keyboard
        for btn in row
        if btn.callback_data == "wp:toggle:session_123"
    ][0]
    assert "Выкл ❌" in wp_btn_no.text



def test_presets_keyboard_structure() -> None:
    from bot.keyboards.theme_keyboards import create_presets_keyboard

    kb = create_presets_keyboard()
    assert len(kb.inline_keyboard) >= 4
    callbacks = [
        btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data
    ]
    assert "preset:apply:cyberpunk_rem" in callbacks
    assert "preset:apply:cyberpunk_ram" in callbacks
    assert "preset:apply:amoled_black" in callbacks
    assert "preset:apply:minimalist_pastel" in callbacks


def test_handle_start() -> None:
    mock_message = AsyncMock()
    asyncio.run(handle_start(mock_message))

    mock_message.answer.assert_awaited_once()
    called_text = mock_message.answer.call_args[0][0]
    assert "Привет! Я генератор тем" in called_text


def test_handle_help() -> None:
    mock_message = AsyncMock()
    asyncio.run(handle_help(mock_message))

    mock_message.answer.assert_awaited_once()
    called_text = mock_message.answer.call_args[0][0]
    assert "Telegram Desktop" in called_text
    assert "Telegram Android" in called_text
    assert "Telegram iOS" in called_text

