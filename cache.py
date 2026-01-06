"""
Redis cache wrapper with JSON serialization and compression support.

Provides high-level cache operations that work with or without Redis.
"""
import json
import gzip
import logging
import os
from typing import Any, Optional, Dict, List
from redis_client import get_redis, is_redis_enabled

logger = logging.getLogger("bot")

# Get config values directly to avoid circular import
REDIS_PREFIX = os.getenv("REDIS_PREFIX", "travistat:")
REDIS_DEFAULT_TTL_SECONDS = int(os.getenv("REDIS_DEFAULT_TTL_SECONDS", "3600"))


def _make_key(key: str) -> str:
    """Create a namespaced cache key."""
    return f"{REDIS_PREFIX}{key}"


def cache_get_str(key: str) -> Optional[str]:
    """
    Get a string value from cache.
    
    Args:
        key: Cache key
        
    Returns:
        Cached string value or None if not found
    """
    redis = get_redis()
    if not redis:
        return None
    
    try:
        full_key = _make_key(key)
        value = redis.get(full_key)
        if value is None:
            return None
        # Decode bytes to string
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return value
    except Exception as e:
        logger.warning(f"Redis get_str failed for key {key}: {e}")
        return None


def cache_set_str(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """
    Set a string value in cache.
    
    Args:
        key: Cache key
        value: String value to cache
        ttl: Time-to-live in seconds (defaults to REDIS_DEFAULT_TTL_SECONDS)
        
    Returns:
        True if successful, False otherwise
    """
    redis = get_redis()
    if not redis:
        return False
    
    try:
        full_key = _make_key(key)
        ttl = ttl or REDIS_DEFAULT_TTL_SECONDS
        redis.setex(full_key, ttl, value.encode('utf-8') if isinstance(value, str) else value)
        return True
    except Exception as e:
        logger.warning(f"Redis set_str failed for key {key}: {e}")
        return False


def cache_get_json(key: str) -> Optional[Any]:
    """
    Get a JSON-serialized value from cache.
    
    Args:
        key: Cache key
        
    Returns:
        Deserialized JSON value (dict/list) or None if not found
    """
    redis = get_redis()
    if not redis:
        return None
    
    try:
        full_key = _make_key(key)
        value = redis.get(full_key)
        if value is None:
            return None
        
        # Decode bytes to string
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        
        return json.loads(value)
    except json.JSONDecodeError as e:
        logger.warning(f"Redis get_json: invalid JSON for key {key}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Redis get_json failed for key {key}: {e}")
        return None


def cache_set_json(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Set a JSON-serialized value in cache.
    
    Args:
        key: Cache key
        value: Value to serialize and cache (must be JSON-serializable)
        ttl: Time-to-live in seconds (defaults to REDIS_DEFAULT_TTL_SECONDS)
        
    Returns:
        True if successful, False otherwise
    """
    redis = get_redis()
    if not redis:
        return False
    
    try:
        full_key = _make_key(key)
        ttl = ttl or REDIS_DEFAULT_TTL_SECONDS
        json_str = json.dumps(value)
        redis.setex(full_key, ttl, json_str.encode('utf-8'))
        return True
    except (TypeError, ValueError) as e:
        logger.warning(f"Redis set_json: failed to serialize value for key {key}: {e}")
        return False
    except Exception as e:
        logger.warning(f"Redis set_json failed for key {key}: {e}")
        return False


def cache_get_gzip_json(key: str) -> Optional[Any]:
    """
    Get a gzip-compressed JSON value from cache.
    
    Args:
        key: Cache key
        
    Returns:
        Deserialized JSON value (dict/list) or None if not found
    """
    redis = get_redis()
    if not redis:
        return None
    
    try:
        full_key = _make_key(key)
        compressed = redis.get(full_key)
        if compressed is None:
            return None
        
        # Decompress
        if isinstance(compressed, str):
            compressed = compressed.encode('latin-1')
        
        decompressed = gzip.decompress(compressed)
        json_str = decompressed.decode('utf-8')
        return json.loads(json_str)
    except Exception as e:
        logger.warning(f"Redis get_gzip_json failed for key {key}: {e}")
        return None


def cache_set_gzip_json(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Set a gzip-compressed JSON value in cache.
    
    Useful for large payloads like markers data.
    
    Args:
        key: Cache key
        value: Value to serialize, compress, and cache (must be JSON-serializable)
        ttl: Time-to-live in seconds (defaults to REDIS_DEFAULT_TTL_SECONDS)
        
    Returns:
        True if successful, False otherwise
    """
    redis = get_redis()
    if not redis:
        return False
    
    try:
        full_key = _make_key(key)
        ttl = ttl or REDIS_DEFAULT_TTL_SECONDS
        
        # Serialize to JSON
        json_str = json.dumps(value)
        json_bytes = json_str.encode('utf-8')
        
        # Compress
        compressed = gzip.compress(json_bytes, compresslevel=6)
        
        redis.setex(full_key, ttl, compressed)
        return True
    except (TypeError, ValueError) as e:
        logger.warning(f"Redis set_gzip_json: failed to serialize value for key {key}: {e}")
        return False
    except Exception as e:
        logger.warning(f"Redis set_gzip_json failed for key {key}: {e}")
        return False


def cache_delete(key: str) -> bool:
    """
    Delete a key from cache.
    
    Args:
        key: Cache key to delete
        
    Returns:
        True if successful, False otherwise
    """
    redis = get_redis()
    if not redis:
        return False
    
    try:
        full_key = _make_key(key)
        redis.delete(full_key)
        return True
    except Exception as e:
        logger.warning(f"Redis delete failed for key {key}: {e}")
        return False


def cache_delete_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern.
    
    WARNING: This can be slow on large databases. Use with caution.
    
    Args:
        pattern: Pattern to match (e.g., "markers:*")
        
    Returns:
        Number of keys deleted
    """
    redis = get_redis()
    if not redis:
        return 0
    
    try:
        full_pattern = _make_key(pattern)
        count = 0
        # Use SCAN to avoid blocking
        cursor = 0
        while True:
            cursor, keys = redis.scan(cursor, match=full_pattern, count=100)
            if keys:
                count += redis.delete(*keys)
            if cursor == 0:
                break
        return count
    except Exception as e:
        logger.warning(f"Redis delete_pattern failed for pattern {pattern}: {e}")
        return 0

