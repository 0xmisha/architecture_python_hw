import json
import os
from typing import Any

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: redis.Redis = redis.from_url(REDIS_URL, decode_responses=True)

HOTEL_TTL = 300  # 5 minutes


def cache_get(key: str) -> Any | None:
    val = _redis.get(key)
    return json.loads(val) if val is not None else None


def cache_set(key: str, value: Any, ttl: int = HOTEL_TTL) -> None:
    _redis.set(key, json.dumps(value, default=str), ex=ttl)


def cache_delete(key: str) -> None:
    _redis.delete(key)


def cache_delete_pattern(pattern: str) -> None:
    keys = list(_redis.scan_iter(pattern))
    if keys:
        _redis.delete(*keys)
