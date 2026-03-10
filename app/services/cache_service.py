from abc import ABC, abstractmethod
from typing import Optional, Any
import time
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 600) -> None:
        pass

class InMemoryCache(CacheService):
    def __init__(self):
        self._cache = {}
        logger.info("Initialized InMemoryCache")

    async def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if entry["expire_at"] > time.time():
                logger.debug(f"Cache HIT for {key}")
                return entry["value"]
            else:
                del self._cache[key]  # Expired
        logger.debug(f"Cache MISS for {key}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 600) -> None:
        self._cache[key] = {
            "value": value,
            "expire_at": time.time() + ttl
        }
        logger.debug(f"Cache SET for {key}, TTL={ttl}s")

class RedisCache(CacheService):
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None
        # Lazy import to avoid crash if redis is not installed
        try:
            import redis.asyncio as redis
            self.redis = redis.from_url(redis_url, decoding_responses=True)
            logger.info(f"Initialized RedisCache at {redis_url}")
        except ImportError:
            logger.error("redis-py not installed. Falling back to InMemoryCache behavior requires fix.")
            raise ImportError("redis-py not installed")

    async def get(self, key: str) -> Optional[Any]:
        try:
            val = await self.redis.get(key)
            if val:
                logger.debug(f"Cache HIT for {key}")
                return json.loads(val) # Assuming JSON storage
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 600) -> None:
        try:
            await self.redis.set(key, json.dumps(value), ex=ttl)
            logger.debug(f"Cache SET for {key}")
        except Exception as e:
            logger.error(f"Redis SET error: {e}")

def get_cache_service() -> CacheService:
    if settings.CACHE_TYPE == "redis":
        try:
            return RedisCache(settings.REDIS_URL)
        except Exception:
            logger.warning("Failed to init RedisCache, falling back to InMemory.")
            return InMemoryCache()
    return InMemoryCache()
