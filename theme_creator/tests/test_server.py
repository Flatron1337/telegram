from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient, TestServer

from bot.server import create_web_app, validate_telegram_init_data


def test_create_web_app_routes() -> None:
    app = create_web_app()
    assert app is not None

    routes = [route.resource.canonical for route in app.router.routes() if route.resource]
    assert "/" in routes
    assert "/health" in routes
    assert "/api/apply-theme" in routes


def test_validate_telegram_init_data() -> None:
    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    user_json = json.dumps({"id": 1337, "first_name": "TestUser"})
    data_dict = {
        "auth_date": "1710000000",
        "query_id": "AAHdF6IQAAAAAN0XohDhrOrc",
        "user": user_json,
    }
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data_dict.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    valid_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    init_data = (
        f"auth_date=1710000000&query_id=AAHdF6IQAAAAAN0XohDhrOrc&user={user_json}&hash={valid_hash}"
    )

    parsed_user = validate_telegram_init_data(init_data, bot_token)
    assert parsed_user is not None
    assert parsed_user.get("id") == 1337

    # Tampered data
    bad_init_data = init_data.replace("1337", "9999")
    assert validate_telegram_init_data(bad_init_data, bot_token) is None
    assert validate_telegram_init_data("", bot_token) is None


def test_apply_theme_api() -> None:
    async def _run() -> None:
        mock_bot = AsyncMock()
        app = create_web_app(bot=mock_bot)

        async with TestClient(TestServer(app)) as client:
            # Test health check
            health_resp = await client.get("/health")
            assert health_resp.status == 200
            health_json = await health_resp.json()
            assert health_json["status"] == "ok"

            # Test apply theme POST
            payload = {
                "user_id": 999888,
                "theme": {
                    "name": "Test Theme",
                    "accent": "#00E5FF",
                    "background": "#0B0E14",
                    "in_bubble": "#16202C",
                    "out_bubble": "#005577",
                    "is_dark": True,
                    "in_bubble_alpha": 200,
                    "out_bubble_alpha": 220,
                },
            }
            post_resp = await client.post("/api/apply-theme", json=payload)
            assert post_resp.status == 200
            post_json = await post_resp.json()
            assert post_json["status"] == "ok"

            # Verify bot sent photo to user
            mock_bot.send_photo.assert_awaited_once()
            call_kwargs = mock_bot.send_photo.await_args.kwargs
            assert call_kwargs["chat_id"] == 999888
            assert "Кастомная тема из Theme Studio готова" in call_kwargs["caption"]

    asyncio.run(_run())
