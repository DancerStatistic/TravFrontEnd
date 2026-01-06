"""
Redis client initialization and health checks.

Provides a Redis client that gracefully handles missing configuration
and connection failures.
"""
import os
import logging
from typing import Optional
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger("bot")

_redis_client: Optional[Redis] = None
_redis_enabled = False


def get_redis() -> Optional[Redis]:
    """
    Get Redis client instance.
    
    Returns:
        Redis client if configured and available, None otherwise
    """
    global _redis_client, _redis_enabled
    
    # If already initialized, return it
    if _redis_client is not None or _redis_enabled is False:
        return _redis_client
    
    # Check if Redis URL is configured
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        logger.info("Redis not configured (REDIS_URL not set), using in-memory cache only")
        _redis_enabled = False
        return None
    
    try:
        # Initialize Redis client from URL
        # redis:// or rediss:// (SSL) URLs are supported
        _redis_client = Redis.from_url(
            redis_url,
            decode_responses=False,  # We'll handle encoding ourselves for binary data
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        _redis_client.ping()
        _redis_enabled = True
        logger.info("✅ Redis client initialized and connected")
        return _redis_client
    except (ConnectionError, TimeoutError, Exception) as e:
        logger.warning(f"Redis connection failed: {e}, falling back to in-memory cache")
        _redis_enabled = False
        _redis_client = None
        return None


def redis_health_check() -> dict:
    """
    Check Redis health status.
    
    Returns:
        Dictionary with status information
    """
    client = get_redis()
    if not client:
        return {
            'status': 'not_configured',
            'reachable': False
        }
    
    try:
        # Ping Redis
        client.ping()
        
        # Get info if available
        info = {}
        try:
            info_data = client.info('memory')
            info['used_memory_mb'] = info_data.get('used_memory', 0) / (1024 * 1024)
        except:
            pass
        
        try:
            info['db_size'] = client.dbsize()
        except:
            pass
        
        return {
            'status': 'ok',
            'reachable': True,
            **info
        }
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return {
            'status': 'unreachable',
            'reachable': False,
            'error': str(e)
        }


def is_redis_enabled() -> bool:
    """Check if Redis is enabled and available."""
    return get_redis() is not None

