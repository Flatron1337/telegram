from __future__ import annotations

from bot.server import create_web_app


def test_create_web_app() -> None:
    app = create_web_app()
    assert app is not None

    routes = [route.resource.canonical for route in app.router.routes() if route.resource]
    assert "/" in routes
    assert "/health" in routes
