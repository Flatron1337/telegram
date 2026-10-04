from __future__ import annotations

import hashlib
import hmac
import json
import logging
from pathlib import Path
from urllib.parse import parse_qsl

from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiohttp import web

from bot.keyboards.theme_keyboards import create_theme_selection_keyboard
from bot.services.session_store import ThemeSessionStore
from bot.services.theme_service import ThemeService

default_theme_service = ThemeService()
default_session_store = ThemeSessionStore()

BOT_KEY: web.AppKey[object] = web.AppKey("bot")
THEME_SVC_KEY: web.AppKey[ThemeService] = web.AppKey("theme_service")
SESS_STORE_KEY: web.AppKey[ThemeSessionStore] = web.AppKey("session_store")
BOT_TOKEN_KEY: web.AppKey[str] = web.AppKey("bot_token")

logger = logging.getLogger("theme_bot.server")


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict | None:
    """Validate Telegram WebApp initData HMAC-SHA256 signature and return user dict if valid."""
    if not init_data or not bot_token:
        return None
    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        provided_hash = parsed.pop("hash", None)
        if not provided_hash:
            return None
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        if hmac.compare_digest(computed_hash, provided_hash):
            user_raw = parsed.get("user")
            return json.loads(user_raw) if user_raw else parsed
        return None
    except Exception:
        return None


def _format_theme_caption(payload: dict, result) -> str:
    """Format caption for generated theme selection message."""
    has_trans = bool(
        payload.get("has_transparency")
        or payload.get("in_bubble_alpha", 255) < 255
        or payload.get("out_bubble_alpha", 255) < 255
    )
    trans_line = "🫧 <b>Прозрачность:</b> Включена ✅\n" if has_trans else ""
    return (
        "✨ <b>Кастомная тема из Theme Studio готова!</b>\n\n"
        f"🎨 <b>Название:</b> {payload.get('name', 'Custom Studio Theme')}\n"
        f"🎯 <b>Акцент:</b> <code>{result.dark_theme.accent.hex.upper()}</code>\n"
        f"🌙 <b>Фон:</b> <code>{result.dark_theme.background.hex.upper()}</code>\n"
        f"{trans_line}\n"
        "Выберите тему для загрузки:"
    )


async def apply_theme_handler(request: web.Request) -> web.Response:
    """Receive custom theme parameters from WebApp and deliver theme package to user chat."""
    bot = request.app.get(BOT_KEY)  # type: ignore[arg-type]
    theme_svc = request.app.get(THEME_SVC_KEY, default_theme_service)
    sess_store = request.app.get(SESS_STORE_KEY, default_session_store)
    token = request.app.get(BOT_TOKEN_KEY, "")

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"status": "error", "message": "Invalid JSON"}, status=400)

    init_data = data.get("init_data")
    user_info = validate_telegram_init_data(init_data, token) if init_data and token else None

    user_id = None
    if user_info and "id" in user_info:
        user_id = user_info["id"]
    elif data.get("user_id"):
        user_id = data.get("user_id")

    payload = data.get("theme") or data
    try:
        result = await theme_svc.process_custom_palette_async(payload)
        session_id = sess_store.create(result)
    except Exception as exc:
        logger.exception("Failed to build custom palette from WebApp payload: %s", exc)
        return web.json_response({"status": "error", "message": str(exc)}, status=500)

    if bot and user_id:
        try:
            caption = _format_theme_caption(payload, result)
            preview_file = BufferedInputFile(
                result.dark_preview_png, filename="preview_studio.png"
            )
            await bot.send_photo(
                chat_id=user_id,
                photo=preview_file,
                caption=caption,
                reply_markup=create_theme_selection_keyboard(session_id, with_wallpaper=False),
            )
            logger.info("Successfully delivered WebApp theme to chat %s", user_id)
        except Exception as exc:
            logger.exception("Failed to send theme to user %s: %s", user_id, exc)
            return web.json_response(
                {"status": "error", "message": f"Could not send to Telegram chat: {exc}"},
                status=500,
            )

    return web.json_response(
        {"status": "ok", "message": "Theme generated and delivered!", "session_id": session_id}
    )


def create_web_app(
    bot: Bot | None = None,
    theme_service: ThemeService | None = None,
    session_store: ThemeSessionStore | None = None,
    bot_token: str | None = None,
) -> web.Application:
    """Build and configure aiohttp web application serving Theme Studio Mini App and API."""
    app = web.Application()
    webapp_dir = Path(__file__).resolve().parent.parent / "webapp"

    app[BOT_KEY] = bot
    app[THEME_SVC_KEY] = theme_service or default_theme_service
    app[SESS_STORE_KEY] = session_store or default_session_store
    app[BOT_TOKEN_KEY] = bot_token or ""

    async def index_handler(_: web.Request) -> web.FileResponse:
        return web.FileResponse(webapp_dir / "index.html")

    async def health_handler(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "app": "telegram-theme-studio"})

    app.router.add_get("/", index_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_post("/api/apply-theme", apply_theme_handler)
    app.router.add_static("/", webapp_dir)

    return app


async def start_web_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    bot: Bot | None = None,
    theme_service: ThemeService | None = None,
    session_store: ThemeSessionStore | None = None,
    bot_token: str | None = None,
) -> web.AppRunner | None:
    """Asynchronously initialize and bind the local Theme Studio HTTP server."""
    try:
        app = create_web_app(
            bot=bot,
            theme_service=theme_service,
            session_store=session_store,
            bot_token=bot_token,
        )
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info("Theme Studio Web App started at http://%s:%d", host, port)
        return runner
    except Exception as exc:
        logger.warning("Could not start local Web App server on %s:%d: %s", host, port, exc)
        return None
