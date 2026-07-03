import asyncio
import json
import time
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.config import config


logger = logging.getLogger(__name__)


class CacheManager:
    """Cache manager with Redis fallback to in-memory cache"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = config.cache_ttl
        self._use_redis = False
    
    async def initialize(self):
        """Initialize cache backend"""
        if REDIS_AVAILABLE and config.redis_url:
            try:
                self.redis_client = redis.from_url(config.redis_url)
                # Test connection
                await self.redis_client.ping()
                self._use_redis = True
                logger.info("Redis cache initialized")
                return True
            except Exception as e:
                logger.warning(f"Redis not available, using memory cache: {e}")
        
        self._use_redis = False
        logger.info("Memory cache initialized")
        return True
    
    async def close(self):
        """Close cache connections"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis cache closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self._use_redis and self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self._get_memory(key)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            
            if self._use_redis and self.redis_client:
                serialized_value = json.dumps(value, default=str)
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                self._set_memory(key, value, ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self._use_redis and self.redis_client:
                await self.redis_client.delete(key)
            else:
                self._delete_memory(key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self._use_redis and self.redis_client:
                return bool(await self.redis_client.exists(key))
            else:
                return self._exists_memory(key)
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self._use_redis and self.redis_client:
                await self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Get time to live for key"""
        try:
            if self._use_redis and self.redis_client:
                return await self.redis_client.ttl(key)
            else:
                return self._get_ttl_memory(key)
        except Exception as e:
            logger.error(f"Error getting TTL for key {key}: {e}")
            return -1
    
    # URL-specific cache methods
    async def cache_url_content(self, url: str, content: str, metadata: Dict[str, Any] = None, ttl: Optional[int] = None) -> bool:
        """Cache URL content"""
        key = f"url:{url}"
        data = {
            'content': content,
            'metadata': metadata or {},
            'cached_at': datetime.utcnow().isoformat(),
        }
        return await self.set(key, data, ttl)
    
    async def get_cached_url_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached URL content"""
        key = f"url:{url}"
        return await self.get(key)
    
    async def cache_parse_result(self, url: str, parse_result: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache parse result"""
        key = f"parse:{url}"
        data = {
            'result': parse_result,
            'cached_at': datetime.utcnow().isoformat(),
        }
        return await self.set(key, data, ttl)
    
    async def get_cached_parse_result(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached parse result"""
        key = f"parse:{url}"
        cached_data = await self.get(key)
        return cached_data.get('result') if cached_data else None
    
    async def cache_robots_txt(self, domain: str, robots_content: str, ttl: Optional[int] = None) -> bool:
        """Cache robots.txt content"""
        key = f"robots:{domain}"
        data = {
            'content': robots_content,
            'cached_at': datetime.utcnow().isoformat(),
        }
        return await self.set(key, data, ttl or 3600)  # Default 1 hour for robots.txt
    
    async def get_cached_robots_txt(self, domain: str) -> Optional[str]:
        """Get cached robots.txt content"""
        key = f"robots:{domain}"
        cached_data = await self.get(key)
        return cached_data.get('content') if cached_data else None
    
    async def cache_domain_delay(self, domain: str, delay: float, ttl: Optional[int] = None) -> bool:
        """Cache domain crawl delay"""
        key = f"delay:{domain}"
        return await self.set(key, delay, ttl or 300)  # Default 5 minutes
    
    async def get_cached_domain_delay(self, domain: str) -> Optional[float]:
        """Get cached domain crawl delay"""
        key = f"delay:{domain}"
        return await self.get(key)
    
    # Statistics and monitoring
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self._use_redis and self.redis_client:
                info = await self.redis_client.info()
                return {
                    'type': 'redis',
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': self._calculate_hit_rate(info),
                }
            else:
                return {
                    'type': 'memory',
                    'total_keys': len(self.memory_cache),
                    'expired_keys': len([k for k, v in self.memory_cache.items() if v.get('expires', 0) < time.time()]),
                }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'type': 'unknown', 'error': str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return (hits / total) * 100
    
    # Memory cache implementation
    def _get_memory(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if item.get('expires', 0) > time.time():
                return item['value']
            else:
                del self.memory_cache[key]
        return None
    
    def _set_memory(self, key: str, value: Any, ttl: int) -> None:
        """Set value in memory cache"""
        expires = time.time() + ttl
        self.memory_cache[key] = {
            'value': value,
            'expires': expires,
        }
        
        # Clean up expired entries periodically
        if len(self.memory_cache) > 1000:  # Clean when cache gets large
            self._cleanup_memory()
    
    def _delete_memory(self, key: str) -> None:
        """Delete key from memory cache"""
        self.memory_cache.pop(key, None)
    
    def _exists_memory(self, key: str) -> bool:
        """Check if key exists in memory cache"""
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if item.get('expires', 0) > time.time():
                return True
            else:
                del self.memory_cache[key]
        return False
    
    def _get_ttl_memory(self, key: str) -> int:
        """Get TTL for key in memory cache"""
        if key in self.memory_cache:
            item = self.memory_cache[key]
            ttl = item.get('expires', 0) - time.time()
            return max(0, int(ttl))
        return -1
    
    def _cleanup_memory(self) -> None:
        """Clean up expired entries from memory cache"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if item.get('expires', 0) <= current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


# Global cache instance
cache = CacheManager()
