"""Rate limiting configuration and utilities."""
from functools import wraps
from flask import request, jsonify


def setup_rate_limiter(app, config):
    """Set up Flask-Limiter for rate limiting."""
    # Return a no-op limiter if rate limiting is disabled or flask-limiter is not installed
    class NoOpLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    
    if not config.RATE_LIMIT_ENABLED:
        return NoOpLimiter()
    
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[config.RATE_LIMIT_DEFAULT],
            storage_uri=config.REDIS_URL if config.REDIS_URL else "memory://",
            strategy="fixed-window"
        )
        
        return limiter
    except ImportError:
        # flask-limiter not installed, return no-op limiter
        import logging
        logger = logging.getLogger("bot")
        logger.warning("flask-limiter not installed. Rate limiting disabled. Install with: pip install flask-limiter")
        return NoOpLimiter()
