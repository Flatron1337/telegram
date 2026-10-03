from __future__ import annotations

import time
from unittest.mock import MagicMock

from bot.services.session_store import ThemeSessionStore
from bot.services.theme_service import ProcessedThemeResult


def create_dummy_theme_result() -> ProcessedThemeResult:
    return ProcessedThemeResult(
        dark_theme=MagicMock(),
        light_theme=MagicMock(),
        dark_preview_png=b"dark_png",
        light_preview_png=b"light_png",
        tdesktop_dark=b"td_dark",
        tdesktop_light=b"td_light",
        android_dark=b"an_dark",
        android_light=b"an_light",
        ios_dark=b"ios_dark",
        ios_light=b"ios_light",
    )



def test_session_store_create_and_get() -> None:
    store = ThemeSessionStore()
    result = create_dummy_theme_result()
    session_id = store.create(result)

    assert isinstance(session_id, str)
    item = store.get(session_id)
    assert item is not None
    assert item.result.dark_preview_png == b"dark_png"
    assert item.current_preview == "dark"


def test_session_store_expiration() -> None:
    store = ThemeSessionStore(ttl_seconds=0.01)
    result = create_dummy_theme_result()
    session_id = store.create(result)

    time.sleep(0.02)
    assert store.get(session_id) is None


def test_session_store_capacity_eviction() -> None:
    store = ThemeSessionStore(max_items=2)
    sid1 = store.create(create_dummy_theme_result())
    sid2 = store.create(create_dummy_theme_result())
    sid3 = store.create(create_dummy_theme_result())

    # First item should be evicted
    assert store.get(sid1) is None
    assert store.get(sid2) is not None
    assert store.get(sid3) is not None
