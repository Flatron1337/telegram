from __future__ import annotations

import pytest
from pydantic import ValidationError

from bot.config import Settings


def test_settings_load_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "fake_token_12345")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "20")

    settings = Settings()
    assert settings.bot_token.get_secret_value() == "fake_token_12345"
    assert "fake_token_12345" not in repr(settings.bot_token)
    assert settings.max_file_size_mb == 20


def test_settings_missing_token_raises_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
