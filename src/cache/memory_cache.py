import time
from typing import Any, Optional, Dict

class MemoryCache:
    """Ultra-fast in-memory cache with automatic TTL expiration."""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        if time.time() > item["expires_at"]:
            del self._store[key]
            return None
        return item["value"]

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        self._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds
        }

    def clear(self) -> None:
        self._store.clear()

cache = MemoryCache()
