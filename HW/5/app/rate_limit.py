import os
import time
from typing import Callable

import redis
from fastapi import HTTPException, Request, Response, status

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: redis.Redis = redis.from_url(REDIS_URL, decode_responses=True)


def make_rate_limiter(key_prefix: str, limit: int, window_seconds: int) -> Callable:
    """
    Returns a FastAPI dependency that enforces sliding-window rate limiting.

    Algorithm: Sliding Window Counter via Redis ZSET.
      - ZADD  key {ns_timestamp: now}      — record this request
      - ZREMRANGEBYSCORE key 0 (now-window) — evict expired entries
      - ZCARD key                           — count requests in window
      - EXPIRE key window+1                 — auto-cleanup

    Headers added on every response:
      X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
    On 429:
      Retry-After is also set.
    """

    def _check(request: Request, response: Response) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key       = f"rl:{key_prefix}:{client_ip}"
        now       = time.time()

        pipe = _redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        pipe.zadd(key, {str(time.time_ns()): now})
        pipe.zcard(key)
        pipe.expire(key, window_seconds + 1)
        results = pipe.execute()

        count     = int(results[2])
        reset_at  = int(now) + window_seconds
        remaining = max(0, limit - count)

        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {limit} requests per {window_seconds}s.",
                headers={
                    "X-RateLimit-Limit":     str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset":     str(reset_at),
                    "Retry-After":           str(window_seconds),
                },
            )

        response.headers["X-RateLimit-Limit"]     = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"]     = str(reset_at)

    return _check
