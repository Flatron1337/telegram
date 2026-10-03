"""Comprehensive Telegram Desktop palette specification based on mature theme tokens."""

from __future__ import annotations

from bot.services.theme_generators.tdesktop_chat_keys import (
    CHAT_SPECS,
    EXTRA_TDESKTOP_SPECS,
)
from bot.services.theme_generators.tdesktop_window_keys import WINDOW_SPECS

TDESKTOP_PALETTE_SPECS: tuple[tuple[str, str], ...] = WINDOW_SPECS + CHAT_SPECS

__all__ = ["EXTRA_TDESKTOP_SPECS", "TDESKTOP_PALETTE_SPECS"]
