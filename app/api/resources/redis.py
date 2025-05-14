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

import json
import logging
from functools import wraps
from fastapi.responses import JSONResponse
from typing import Callable, Awaitable, Any, Optional

from core.config import REDIS_HOST, REDIS_PORT, ENABLE_REDIS_CACHE

logger = logging.getLogger("redis_cache")
logger.setLevel(logging.INFO)


redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def redis_cache_old(key: str, ttl: int = 300):
    """
    A decorator to cache the output of a FastAPI route handler using Redis,
    with a static cache key and configurable TTL.

    Args:
        key (str): The Redis key under which the cached response will be stored.
        ttl (int, optional): Time-to-live in seconds for the cache. Defaults to 300 seconds (5 minutes).

    Returns:
        Callable: The wrapped async route function with caching enabled.

    Example:
        @redis_cache(key="popular_species", ttl=60)
        async def get_popular_species(request: Request):
            ...
    """

    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not ENABLE_REDIS_CACHE:
                logger.info(f"Caching DISABLED — calling {func.__name__} directly.")
                return await func(*args, **kwargs)

            try:
                # Attempt to retrieve cached response
                cached_value = await redis_client.get(key)
                if cached_value is not None:
                    logger.info(f"Cache HIT for key: {key}")
                    return JSONResponse(content=json.loads(cached_value))

                # Call the original function if cache miss
                logger.info(f"Cache MISS for key: {key}")
                result = await func(*args, **kwargs)

                # Cache only if result is a JSONResponse
                if isinstance(result, JSONResponse):
                    content = (
                        result.body.decode()
                        if hasattr(result.body, "decode")
                        else result.body
                    )
                    await redis_client.setex(key, ttl, content)
                    logger.info(f"Cache SET for key: {key} (TTL: {ttl}s)")

                return result

            # /!\ Fallback to normal execution in case there is an issue connecting to redis
            except Exception as e:
                logger.error(f"Redis cache error for key '{key}': {e}")
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def redis_cache(key_prefix: str, arg_keys: Optional[list[str]] = None, ttl: int = 3000):
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
            if not ENABLE_REDIS_CACHE:
                logger.info(f"Caching DISABLED — calling {func.__name__} directly.")
                return await func(*args, **kwargs)

            try:
                # Build dynamic key: prefix + arg values (if any)
                if arg_keys:
                    arg_values = [str(kwargs.get(k, "null")) for k in arg_keys]
                    full_key = key_prefix + ":" + ":".join(arg_values)
                else:
                    full_key = key_prefix

                # Attempt to retrieve cached response
                cached_value = await redis_client.get(full_key)
                if cached_value is not None:
                    logger.info(f"Cache HIT for key: {full_key}")
                    return JSONResponse(content=json.loads(cached_value))

                logger.info(f"Cache MISS for key: {full_key}")
                result = await func(*args, **kwargs)

                if isinstance(result, JSONResponse):
                    content = (
                        result.body.decode()
                        if hasattr(result.body, "decode")
                        else result.body
                    )
                    await redis_client.setex(full_key, ttl, content)
                    logger.info(f"Cache SET for key: {full_key} (TTL: {ttl}s)")

                return result

            # /!\ Fallback to normal execution in case there is an issue connecting to redis
            except Exception as e:
                logger.error(f"Redis cache error for key '{key_prefix}': {e}")
                return await func(*args, **kwargs)

        return wrapper
    return decorator
