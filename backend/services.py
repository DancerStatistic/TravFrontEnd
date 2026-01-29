"""Business logic and data access services."""
import logging
import requests
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional
from supabase import Client
from backend.cache_manager import SQLCacheManager, SupabaseCacheManager
from cache import cache_get_str, cache_set_str

logger = logging.getLogger("bot")


class DataService:
    """Service for data access operations."""
    
    def __init__(
        self,
        supabase_client: Client,
        sql_cache_manager: SQLCacheManager,
        supabase_cache_manager: SupabaseCacheManager,
        config
    ):
        """
        Initialize data service.
        
        Args:
            supabase_client: Supabase client instance
            sql_cache_manager: SQL cache manager
            supabase_cache_manager: Supabase cache manager
            config: Application configuration
        """
        self.supabase = supabase_client
        self.sql_cache = sql_cache_manager
        self.supabase_cache = supabase_cache_manager
        self.config = config
    
    def get_latest_dump_date(self) -> str:
        """
        Get the latest dump_date from Redis cache or Supabase RPC.
        
        Caches the result in Redis for 300 seconds to reduce Supabase calls.
        Falls back to today's date if Supabase is unreachable and cache is empty.
        """
        cached_date = cache_get_str("latest_dump_date")
        if cached_date:
            logger.debug(f"Latest dump_date from Redis cache: {cached_date}")
            return cached_date
        
        # Query Supabase via RPC
        if self._supabase_reachable(1.0):
            try:
                resp = self.supabase.rpc("rpc_latest_dump_date", {}).execute()
                latest = self._rpc_scalar(resp, "rpc_latest_dump_date")
                if latest:
                    latest_str = latest.isoformat() if hasattr(latest, "isoformat") else str(latest)
                    cache_set_str("latest_dump_date", latest_str, ttl=300)
                    logger.info(f"Latest dump_date from Supabase RPC: {latest_str}")
                    return latest_str
                else:
                    logger.warning("rpc_latest_dump_date returned no value (NULL).")
            except Exception as e:
                logger.warning(f"Failed to get latest dump_date from Supabase RPC: {e}")
        
        today = date.today().isoformat()
        logger.warning(f"Using fallback dump_date: {today}")
        return today
    
    def _supabase_reachable(self, timeout: float = 1.0) -> bool:
        """Quick TCP check so we don't block inside httpx when DNS or outbound connectivity is broken."""
        try:
            from urllib.parse import urlparse
            import socket
            host = urlparse(self.config.SUPABASE_URL).hostname
            if not host:
                return False
            with socket.create_connection((host, 443), timeout=timeout):
                return True
        except Exception:
            return False
    
    def _rpc_scalar(self, resp, key: str):
        """
        Supabase RPC responses can come back as:
          - resp.data == [{"<key>": value}]  (common for SQL functions returning scalar)
          - resp.data == value              (sometimes)
        This helper normalizes both cases.
        """
        data = getattr(resp, "data", None)
        if data is None:
            return None
        if isinstance(data, list):
            if not data:
                return None
            row = data[0]
            if isinstance(row, dict):
                return row.get(key)
            return row
        if isinstance(data, dict):
            return data.get(key)
        return data
    
    def fetch_supabase_data(self) -> List[Dict[str, Any]]:
        """
        Fetch village data from Supabase with caching and pagination.
        
        Uses in-memory cache to avoid repeated database queries. Falls back gracefully
        if Supabase is unreachable. Implements pagination to handle large datasets.
        
        Returns:
            List of village dictionaries, or empty list if fetch fails
        """
        # Check cache first
        cached = self.supabase_cache.get()
        if cached:
            return cached
        
        # Fast-fail: skip Supabase entirely if we can't reach it
        if not self._supabase_reachable(1.0):
            logger.warning("Supabase precheck failed; skipping remote fetch.")
            return []
        
        try:
            resp = (self.supabase.table("villages")
                            .select("dump_date")
                            .order("dump_date", desc=True)
                            .limit(1)
                            .execute())
            dates = resp.data or []
            if not dates:
                return []
            
            latest = dates[0]["dump_date"]
            all_rows: List[Dict[str, Any]] = []
            page_size, offset = 1000, 0
            while True:
                chunk = (self.supabase.table("villages")
                                .select("*")
                                .eq("dump_date", latest)
                                .range(offset, offset+page_size-1)
                                .execute()
                                .data) or []
                all_rows.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
            
            self.supabase_cache.set(all_rows)
            logger.info(f"Fetched {len(all_rows)} rows from Supabase for {latest}")
            return all_rows
        except Exception as e:
            logger.error(f"Supabase fetch failed: {e}")
            return []
