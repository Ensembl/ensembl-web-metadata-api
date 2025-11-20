"""
See the NOTICE file distributed with this work for additional information
regarding copyright ownership.


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import redis.asyncio as redis

import ujson as json
import logging
from functools import wraps
from fastapi.responses import JSONResponse
from typing import Callable, Awaitable, Any, Optional

from redis.asyncio import ConnectionPool

from core.config import REDIS_HOST, REDIS_PORT, ENABLE_REDIS_CACHE, REDIS_MAX_CONNECTION

logger = logging.getLogger("redis_cache")
logger.setLevel(logging.INFO)


redis_pool = ConnectionPool.from_url(
    f"redis://{REDIS_HOST}:{REDIS_PORT}",
    max_connections=int(REDIS_MAX_CONNECTION),
    decode_responses=True
)

redis_client = redis.Redis(connection_pool=redis_pool)


def redis_cache(key_prefix: str, arg_keys: Optional[list[str]] = None, ttl: int = 300):
    """
    A decorator to cache the output of a FastAPI route handler using Redis,
    with dynamic key generation based on route args.

    Args:
        key_prefix (str): Static part of the Redis key (e.g., "example_objects").
        arg_keys (list[str], optional): List of argument names to append to the key.
        ttl (int, optional): Time-to-live in seconds for the cache. Defaults to 300 seconds.

    Returns:
        Callable: The decorated async route function.

    Example:
        @redis_cache("example_objects", arg_keys=["genome_id"])
        async def example_objects(request: Request, genome_id: str):
            ...
    """
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build dynamic key: prefix + arg values (if any)
            if arg_keys:
                separator = "\x00"
                arg_values = [str(kwargs.get(k, "null")) for k in arg_keys]
                full_key = key_prefix + separator + separator.join(arg_values)
            else:
                full_key = key_prefix

            if not ENABLE_REDIS_CACHE:
                logger.debug("Caching DISABLED — calling %s directly.", func.__name__)
                return await func(*args, **kwargs)

            try:
                # decode full_key for debugging purposes
                safe_key = full_key.replace("\x00", ":")

                # Attempt to retrieve cached response
                cached_value = await redis_client.get(full_key)
                if cached_value is not None:
                    logger.debug("Cache HIT for key: %s", safe_key)
                    return JSONResponse(content=json.loads(cached_value))

                logger.debug("Cache MISS for key: %s", safe_key)
                result = await func(*args, **kwargs)

                if isinstance(result, JSONResponse):
                    content = (
                        result.body.decode()
                        if hasattr(result.body, "decode")
                        else result.body
                    )
                    await redis_client.setex(full_key, ttl, content)
                    logger.debug("Cache SET for key: %s (TTL: %s s)", safe_key, ttl)

                return result

            # /!\ Fallback to normal execution in case there is an issue connecting to redis
            except Exception as e:
                logger.error(f"Redis cache error for key '{full_key}': {e}")
                return await func(*args, **kwargs)

        return wrapper
    return decorator


async def close_redis_pool():
    """Close the Redis connection pool"""
    await redis_pool.disconnect()
    logger.info("Redis connection pool closed")
