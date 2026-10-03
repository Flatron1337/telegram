from __future__ import annotations

import logging
from pathlib import Path

from aiohttp import web

logger = logging.getLogger("theme_bot.server")


def create_web_app() -> web.Application:
    """Build and configure aiohttp web application serving Theme Studio Mini App."""
    app = web.Application()
    webapp_dir = Path(__file__).resolve().parent.parent / "webapp"

    async def index_handler(_: web.Request) -> web.FileResponse:
        return web.FileResponse(webapp_dir / "index.html")

    async def health_handler(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "app": "telegram-theme-studio"})

    app.router.add_get("/", index_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_static("/", webapp_dir)

    return app


async def start_web_server(host: str = "0.0.0.0", port: int = 8080) -> web.AppRunner | None:
    """Asynchronously initialize and bind the local Theme Studio HTTP server."""
    try:
        app = create_web_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info("Theme Studio Web App started at http://%s:%d", host, port)
        return runner
    except Exception as exc:
        logger.warning("Could not start local Web App server on %s:%d: %s", host, port, exc)
        return None
