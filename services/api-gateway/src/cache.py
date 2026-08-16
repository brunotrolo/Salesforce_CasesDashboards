"""Redis caching service for API Gateway."""

import os
import json
import logging
from typing import Optional, Any
from datetime import timedelta

import redis

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "60"))


class CacheService:
    """Service for caching operations with Redis."""

    def __init__(self, redis_url: str = REDIS_URL):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache will be disabled.")
            self.redis_client = None
            self.available = False

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.available:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl_minutes: int = CACHE_TTL_MINUTES) -> bool:
        """Set value in cache with TTL."""
        if not self.available:
            return False

        try:
            serialized = json.dumps(value)
            self.redis_client.setex(
                key,
                timedelta(minutes=ttl_minutes),
                serialized
            )
            logger.debug(f"Cache set: {key} (TTL: {ttl_minutes}m)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.available:
            return False

        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.available:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cache cleared: {len(keys)} keys matching '{pattern}'")
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0


# Global cache instance
cache = CacheService()


def get_cache_key(prefix: str, *args) -> str:
    """Generate cache key from prefix and arguments."""
    key_parts = [prefix] + [str(arg) for arg in args]
    return ":".join(key_parts)
