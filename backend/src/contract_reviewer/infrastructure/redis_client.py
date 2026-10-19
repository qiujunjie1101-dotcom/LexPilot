"""Redis 缓存与 Pub/Sub 事件发布订阅客户端（未配置 REDIS_URL 时不启用）。"""
from __future__ import annotations

import os
from typing import Any


class RedisEventBus:
    def __init__(self, url: str) -> None:
        self.url = url

    def _client(self) -> Any:
        try:
            import redis
        except ImportError as exc:
            raise RuntimeError('REDIS_URL requires the optional "redis" package') from exc
        return redis.Redis.from_url(self.url, decode_responses=True)

    def publish(self, channel: str, message: str) -> int:
        return int(self._client().publish(channel, message))

    def ping(self) -> bool:
        return bool(self._client().ping())


def get_event_bus() -> RedisEventBus | None:
    url = os.getenv('REDIS_URL', '').strip()
    return RedisEventBus(url) if url else None
