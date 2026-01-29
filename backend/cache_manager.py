"""Thread-safe cache manager for SQL and Supabase data."""
import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger("bot")


class SQLCacheManager:
    """Thread-safe cache manager for SQL dump data."""
    
    def __init__(self, ttl: timedelta):
        """
        Initialize SQL cache manager.
        
        Args:
            ttl: Time-to-live for cached data
        """
        self._ttl = ttl
        self._lock = threading.Lock()
        self._cached_sql: List[List[Optional[str]]] = []
        self._last_sql_time = datetime.min
    
    def get(self) -> List[List[Optional[str]]]:
        """
        Get cached SQL data if still valid.
        
        Returns:
            Cached SQL rows or empty list if cache expired/missing
        """
        with self._lock:
            now = datetime.utcnow()
            if self._cached_sql and (now - self._last_sql_time) < self._ttl:
                return self._cached_sql
            return []
    
    def set(self, data: List[List[Optional[str]]]) -> None:
        """
        Set cached SQL data.
        
        Args:
            data: SQL rows to cache
        """
        with self._lock:
            self._cached_sql = data
            self._last_sql_time = datetime.utcnow()
    
    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cached_sql = []
            self._last_sql_time = datetime.min
    
    def is_valid(self) -> bool:
        """Check if cache is still valid."""
        with self._lock:
            now = datetime.utcnow()
            return bool(self._cached_sql and (now - self._last_sql_time) < self._ttl)


class SupabaseCacheManager:
    """Thread-safe cache manager for Supabase data."""
    
    def __init__(self, ttl: timedelta):
        """
        Initialize Supabase cache manager.
        
        Args:
            ttl: Time-to-live for cached data
        """
        self._ttl = ttl
        self._lock = threading.Lock()
        self._cached_date = datetime.min
        self._cached_rows: List[Dict[str, Any]] = []
    
    def get(self) -> List[Dict[str, Any]]:
        """
        Get cached Supabase data if still valid.
        
        Returns:
            Cached rows or empty list if cache expired/missing
        """
        with self._lock:
            now = datetime.utcnow()
            if self._cached_rows and (now - self._cached_date) < self._ttl:
                return self._cached_rows
            return []
    
    def set(self, data: List[Dict[str, Any]]) -> None:
        """
        Set cached Supabase data.
        
        Args:
            data: Rows to cache
        """
        with self._lock:
            self._cached_rows = data
            self._cached_date = datetime.utcnow()
    
    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cached_rows = []
            self._cached_date = datetime.min
    
    def is_valid(self) -> bool:
        """Check if cache is still valid."""
        with self._lock:
            now = datetime.utcnow()
            return bool(self._cached_rows and (now - self._cached_date) < self._ttl)
