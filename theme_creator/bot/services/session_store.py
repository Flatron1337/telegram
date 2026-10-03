from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from uuid import uuid4

from bot.services.theme_service import ProcessedThemeResult


@dataclass(slots=True)
class SessionItem:
    result: ProcessedThemeResult
    current_preview: str  # "dark" or "light"
    created_at: float
    with_wallpaper: bool = True


class ThemeSessionStore:
    """In-memory cache for generated theme results with automatic expiration."""

    def __init__(self, max_items: int = 150, ttl_seconds: float = 3600.0) -> None:
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, SessionItem] = OrderedDict()

    def create(self, result: ProcessedThemeResult) -> str:
        """Store theme result and return generated unique session id."""
        self._cleanup()
        session_id = uuid4().hex[:12]
        self._store[session_id] = SessionItem(
            result=result,
            current_preview="dark",
            created_at=time.time(),
        )
        return session_id

    def get(self, session_id: str) -> SessionItem | None:
        """Retrieve active session by id if not expired."""
        item = self._store.get(session_id)
        if item is None:
            return None
        if time.time() - item.created_at > self.ttl_seconds:
            self._store.pop(session_id, None)
            return None
        self._store.move_to_end(session_id)
        return item

    def _cleanup(self) -> None:
        now = time.time()
        expired = [
            sid for sid, item in self._store.items() if now - item.created_at > self.ttl_seconds
        ]
        for sid in expired:
            self._store.pop(sid, None)

        while len(self._store) >= self.max_items:
            self._store.popitem(last=False)
