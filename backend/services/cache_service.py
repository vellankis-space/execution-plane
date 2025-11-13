"""
Caching service with Redis support
"""
import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")


class CacheService:
    """Service for caching with Redis or in-memory fallback"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {e}, using in-memory cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Error getting from Redis cache: {e}")
        
        # Fallback to memory cache
        if key in self.memory_cache:
            value, expiry = self.memory_cache[key]
            if expiry is None or expiry > datetime.utcnow():
                return value
            else:
                del self.memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache"""
        if self.redis_client:
            try:
                json_value = json.dumps(value)
                if ttl_seconds:
                    self.redis_client.setex(key, ttl_seconds, json_value)
                else:
                    self.redis_client.set(key, json_value)
                return
            except Exception as e:
                logger.warning(f"Error setting Redis cache: {e}")
        
        # Fallback to memory cache
        expiry = None
        if ttl_seconds:
            expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        self.memory_cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """Delete key from cache"""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Error deleting from Redis cache: {e}")
        
        if key in self.memory_cache:
            del self.memory_cache[key]
    
    def clear(self, pattern: Optional[str] = None):
        """Clear cache (optionally by pattern)"""
        if self.redis_client:
            try:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                else:
                    self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Error clearing Redis cache: {e}")
        
        if pattern:
            # Simple pattern matching for memory cache
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace("*", "") in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
        else:
            self.memory_cache.clear()

