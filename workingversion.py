import os
import re
import json
import logging
import time
import requests
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from functools import wraps
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, request, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_cors import CORS
from supabase import create_client, Client
from cachetools import TTLCache
from redis_client import get_redis, redis_health_check, is_redis_enabled
from cache import (
    cache_get_json, cache_set_json, cache_get_gzip_json, cache_set_gzip_json,
    cache_get_str, cache_set_str, cache_delete
)

# Load environment variables
load_dotenv()

# -------------------- Cache Variables -------------------- #
_cached_sql: List[List[Optional[str]]] = []
_last_sql_time = datetime.min
_cached_date = datetime.min
_cached_rows: List[Dict[str, Any]] = []

# -------------------- Configuration -------------------- #
@dataclass
class Config:
    # Flask Configuration
    FLASK_SECRET: str = os.getenv("FLASK_SECRET", "dev-secret")
    PERMANENT_SESSION_LIFETIME: int = 3600  # 1 hour in seconds
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")
    )
    
    # Supabase Configuration
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    SQL_CACHE_TTL: int = int(os.getenv("SQL_CACHE_TTL", "86400"))  # 24 hours
    PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", "1000"))  # Default page size for pagination
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    REDIS_PREFIX: str = os.getenv("REDIS_PREFIX", "travistat:")
    REDIS_DEFAULT_TTL_SECONDS: int = int(os.getenv("REDIS_DEFAULT_TTL_SECONDS", "3600"))  # 1 hour
    
    # Map Configuration
    SQL_FILE_URL: str = os.getenv("SQL_FILE_URL", "https://cw.x2.international.travian.com/map.sql")
    
    def validate(self) -> None:
        """Validate required configuration values."""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY environment variable is required")
        # Redis is optional - will fallback to in-memory cache if not configured

# Initialize config
config = Config()
try:
    config.validate()
    logger = logging.getLogger("bot")
    logger.info("Configuration loaded successfully")
except ValueError as e:
    logging.error(f"Configuration error: {e}")
    raise

# -------------------- Error Handling -------------------- #
class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: int = 400, payload: Optional[Dict] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self) -> Dict[str, Any]:
        rv = dict(self.payload or {})
        rv['message'] = self.message
        rv['status'] = 'error'
        rv['code'] = self.status_code
        rv['timestamp'] = datetime.utcnow().isoformat()
        return rv

def handle_api_error(error: APIError):
    """Convert APIError to JSON response."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def api_error_handler(f):
    """Decorator to handle API errors."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            return handle_api_error(e)
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return handle_api_error(APIError("Internal server error", 500))
    return decorated_function

# -------------------- Input Validation -------------------- #
def validate_pagination_params(page: int, per_page: int, max_per_page: int = 1000) -> Tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        per_page: Items per page
        max_per_page: Maximum allowed items per page
        
    Returns:
        Tuple of (validated_page, validated_per_page)
        
    Raises:
        APIError: If validation fails
    """
    if page < 1:
        raise APIError("Page number must be >= 1", 400)
    if per_page < 1:
        raise APIError("Items per page must be >= 1", 400)
    if per_page > max_per_page:
        raise APIError(f"Items per page cannot exceed {max_per_page}", 400)
    return page, per_page

def validate_string_param(value: str, param_name: str, min_length: int = 1, max_length: int = 1000) -> str:
    """
    Validate string parameters.
    
    Args:
        value: String value to validate
        param_name: Name of the parameter (for error messages)
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Validated and sanitized string
        
    Raises:
        APIError: If validation fails
    """
    if not isinstance(value, str):
        raise APIError(f"{param_name} must be a string", 400)
    value = value.strip()
    if len(value) < min_length:
        raise APIError(f"{param_name} must be at least {min_length} characters", 400)
    if len(value) > max_length:
        raise APIError(f"{param_name} must be at most {max_length} characters", 400)
    return value

# -------------------- Response Formatting -------------------- #
def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Standardized response dictionary
    """
    response = {
        'status': 'success',
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data is not None:
        response['data'] = data
    return response, status_code

def paginated_response(items: List[Any], page: int, per_page: int, total: int) -> Dict[str, Any]:
    """
    Create a standardized paginated response.
    
    Args:
        items: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        
    Returns:
        Standardized paginated response dictionary
    """
    total_pages = (total + per_page - 1) // per_page
    return {
        'status': 'success',
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        },
        'timestamp': datetime.utcnow().isoformat()
    }

# -------------------- Caching -------------------- #
class CacheManager:
    """
    Cache manager with TTL and size limits.
    
    Provides in-memory caching with automatic expiration and statistics tracking.
    """
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            maxsize: Maximum number of items in cache
            ttl: Time-to-live in seconds
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.hits = 0
        self.misses = 0
        
    def get(self, key: str) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        value = self.cache.get(key, None)
        if value is not None:
            self.hits += 1
        else:
            self.misses += 1
        return value
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = value
        
    def clear(self) -> None:
        """Clear the cache and reset statistics."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics (hits, misses, size, hit_ratio)
        """
        total = self.hits + self.misses
        return {
            'hits': self.hits,
            'misses': self.misses,
            'size': len(self.cache),
            'hit_ratio': self.hits / total if total > 0 else 0
        }

# Initialize caches
supabase_cache = CacheManager(ttl=config.CACHE_TTL)
sql_cache = CacheManager(ttl=config.SQL_CACHE_TTL)

from urllib.parse import urlparse
import socket

# -------------------- Logging -------------------- #
class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure structured logging
file_handler = logging.FileHandler("web_app.log", encoding="utf-8")
stream_handler = logging.StreamHandler()

# Use structured format for file, simple format for console
file_handler.setFormatter(StructuredFormatter())
stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger("bot")
load_dotenv() 
# -------------------- Flask & CORS Setup (MUST be before any @app.route) -------------------- #
# -------------------- Flask & CORS Setup -------------------- #
app = Flask(__name__)
app.secret_key = config.FLASK_SECRET
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=config.PERMANENT_SESSION_LIFETIME)
app.config["DEBUG"] = config.DEBUG

# Configure CORS with allowed origins from config
CORS(app, resources={
    r"/*": {
        "origins": config.CORS_ORIGINS,
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

# Register error handlers
@app.errorhandler(404)
def not_found_error(error):
    return handle_api_error(APIError("Resource not found", 404))

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {str(error)}", exc_info=True)
    return handle_api_error(APIError("Internal server error", 500))

# -------------------- Login Manager -------------------- #
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id: str) -> None:
        self.id = id

_users = {"admin@example.com": {"password": "password123"}}

@login_manager.user_loader
def load_user(uid: str) -> Optional[User]:
    return User(uid) if uid in _users else None

# -------------------- Supabase Setup -------------------- #
# Initialize Supabase client using the config
if not config.SUPABASE_URL or not config.SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")

# Create Supabase client
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
logger.info("✅ Supabase client initialized")

# -------------------- Supabase Cache -------------------- #
CACHE_TTL     = timedelta(hours=1)
_cached_date  = datetime.min
_cached_rows: List[Dict[str,Any]] = []

# -------------------- Latest Dump Date Resolver -------------------- #
def get_latest_dump_date() -> str:
    """
    Get the latest dump_date from Redis cache or Supabase.
    
    Caches the result in Redis for 300 seconds to reduce Supabase queries.
    Falls back to today's date if Supabase is unreachable and cache is empty.
    
    Returns:
        Latest dump_date as ISO format string
    """
    # Try Redis cache first
    cached_date = cache_get_str("latest_dump_date")
    if cached_date:
        logger.debug(f"Latest dump_date from Redis cache: {cached_date}")
        return cached_date
    
    # Query Supabase if reachable
    if supabase_reachable(1.0):
        try:
            resp = (supabase.table("villages")
                            .select("dump_date")
                            .order("dump_date", desc=True)
                            .limit(1)
                            .execute())
            dates = resp.data or []
            if dates:
                latest = dates[0]["dump_date"]
                # Cache for 5 minutes
                cache_set_str("latest_dump_date", latest, ttl=300)
                logger.info(f"Latest dump_date from Supabase: {latest}")
                return latest
        except Exception as e:
            logger.warning(f"Failed to get latest dump_date from Supabase: {e}")
    
    # Fallback to today's date
    today = date.today().isoformat()
    logger.warning(f"Using fallback dump_date: {today}")
    return today

def supabase_reachable(timeout: float = 1.0) -> bool:
    """
    Quick TCP check so we don't block inside httpx when DNS or outbound
    connectivity is broken. Returns False in ~1s instead of hanging.
    """
    try:
        host = urlparse(config.SUPABASE_URL).hostname
        if not host:
            return False
        with socket.create_connection((host, 443), timeout=timeout):
            return True
    except Exception:
        return False

def fetch_supabase_data() -> List[Dict[str,Any]]:
    """
    Fetch village data from Supabase with caching and pagination.
    
    Uses in-memory cache to avoid repeated database queries. Falls back gracefully
    if Supabase is unreachable. Implements pagination to handle large datasets.
    
    Returns:
        List of village dictionaries, or empty list if fetch fails
    """
    global _cached_date, _cached_rows
    now = datetime.utcnow()
    if _cached_rows and (now - _cached_date) < CACHE_TTL:
        return _cached_rows

    # ⬇️ fast-fail: skip Supabase entirely if we can't reach it
    if not supabase_reachable(1.0):
        logger.warning("Supabase precheck failed; skipping remote fetch.")
        return []

    try:
        resp = (supabase.table("villages")
                        .select("dump_date")
                        .order("dump_date", desc=True)
                        .limit(1)
                        .execute())
        dates = resp.data or []
        if not dates:
            return []

        latest = dates[0]["dump_date"]
        all_rows: List[Dict[str,Any]] = []
        page_size, offset = 1000, 0
        while True:
            chunk = (supabase.table("villages")
                            .select("*")
                            .eq("dump_date", latest)
                            .range(offset, offset+page_size-1)
                            .execute()
                            .data) or []
            all_rows.extend(chunk)
            if len(chunk) < page_size:
                break
            offset += page_size

        _cached_date, _cached_rows = now, all_rows
        logger.info("Fetched %d rows from Supabase for %s", len(all_rows), latest)
        return all_rows
    except Exception as e:
        logger.error("Supabase fetch failed: %s", e)
        return []



# -------------------- SQL Dump Setup -------------------- #
SQL_FILE_URL   = "https://cw.x2.international.travian.com/map.sql"
SQL_CACHE_TTL  = timedelta(hours=24)
_last_sql_time = datetime.min
_cached_sql: List[List[Optional[str]]] = []
EXPECTED_COLS  = 16

def extract_value_groups(body: str) -> List[str]:
    """
    Extract parenthesized value groups from SQL INSERT statement body.
    
    Handles nested parentheses and escaped quotes correctly.
    
    Args:
        body: SQL INSERT VALUES clause body
        
    Returns:
        List of value group strings (with parentheses)
    """
    groups, depth, in_str, cur, i = [], 0, False, "", 0
    while i < len(body):
        c = body[i]
        if in_str:
            if c=="'" and i+1<len(body) and body[i+1]=="'":
                cur += "''"; i += 2; continue
            if c=="'":
                in_str = False
            cur += c; i += 1
        else:
            if c=="'":
                in_str = True; cur += c; i += 1; continue
            if c=="(":
                if depth == 0: cur=""
                depth += 1
            if depth > 0:
                cur += c
            if c==")" and depth>0:
                depth -= 1
                if depth==0:
                    groups.append(cur)
            i += 1
    return groups

def parse_sql_row(inner: str) -> List[Optional[str]]:
    """
    Parse a single SQL row value group into a list of field values.
    
    Handles quoted strings, escaped quotes, NULL values, and boolean values.
    
    Args:
        inner: Value group string (without outer parentheses)
        
    Returns:
        List of parsed field values (strings, None for NULL, or "TRUE"/"FALSE")
    """
    fields, cur, in_str, i = [], "", False, 0
    while i < len(inner):
        c = inner[i]
        if in_str:
            if c=="'" and i+1<len(inner) and inner[i+1]=="'":
                cur += "''"; i += 2; continue
            if c=="'":
                in_str=False
            cur += c; i += 1
        else:
            if c=="'":
                in_str = True; cur += c; i += 1; continue
            if c==",":
                fields.append(cur); cur=""; i += 1; continue
            cur += c; i += 1
    fields.append(cur)
    norm: List[Optional[str]] = []
    for f in fields:
        s = f.strip()
        if s.upper()=="NULL":
            norm.append(None)
        elif s.upper() in ("TRUE","FALSE"):
            norm.append(s.upper())
        else:
            norm.append(s)
    return norm

def fetch_sql_data() -> List[List[Optional[str]]]:
    """
    Fetch and parse SQL dump file with caching.
    
    Downloads the SQL dump from the configured URL, parses INSERT statements,
    and caches the results. Returns cached data if still valid.
    
    Returns:
        List of parsed SQL rows (each row is a list of field values)
    """
    global _last_sql_time, _cached_sql
    now = datetime.utcnow()
    if _cached_sql and (now - _last_sql_time) < SQL_CACHE_TTL:
        return _cached_sql

    try:
        res = requests.get(SQL_FILE_URL, timeout=15)
        res.raise_for_status()
        text = res.text
    except Exception as e:
        logger.error("Failed to download SQL dump: %s", e)
        return _cached_sql

    rows: List[List[Optional[str]]] = []
    for line in text.splitlines():
        if not line.startswith("INSERT"):
            continue
        body = line.split("VALUES", 1)[1].rstrip(";\n")
        for grp in extract_value_groups(body):
            inner = grp[1:-1]
            cols = parse_sql_row(inner)
            if len(cols) != EXPECTED_COLS:
                logger.warning("Skipping SQL row with %d cols (expected %d)", len(cols), EXPECTED_COLS)
                continue
            rows.append(cols)

    _cached_sql, _last_sql_time = rows, now
    logger.info("Parsed %d rows from SQL dump", len(rows))
    return rows

# -------------------- SQL→Dict Conversion -------------------- #
def strip_quotes(s: Optional[str]) -> Optional[str]:
    """
    Remove surrounding quotes from a string and handle escaped quotes.
    
    Args:
        s: String that may be quoted
        
    Returns:
        Unquoted string or original value if not quoted
    """
    if not s: return s
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1].replace("''", "'")
    return s

def parse_int(v: Optional[str]) -> int:
    """
    Parse a string value to integer with safe fallback.
    
    Args:
        v: String value to parse (may be None)
        
    Returns:
        Parsed integer or 0 if parsing fails
    """
    try: return int(float(v)) if v is not None else 0
    except: return 0

def parse_bool(v: Optional[str]) -> bool:
    """
    Parse a string value to boolean.
    
    Handles "TRUE", "FALSE", "1", "0", and None values.
    
    Args:
        v: String value to parse (may be None)
        
    Returns:
        Boolean value (False for None or invalid values)
    """
    if v is None: return False
    s = v.upper()
    if s in ("1","0"): return bool(int(s))
    return s == "TRUE"

def sql_row_to_dict(r: List[Optional[str]]) -> Dict[str,Any]:
    """
    Convert a parsed SQL row to a dictionary with typed fields.
    
    Maps SQL dump columns to dictionary keys with appropriate type conversion.
    Expected columns: field_id, x, y, tribe, village_id, village_name, player_id,
    player_name, alliance_id, alliance_tag, population, region, capital, city,
    harbor, victory_points (16 total).
    
    Args:
        r: List of field values from parsed SQL row
        
    Returns:
        Dictionary with village data
    """
    return {
        "field_id":      parse_int(r[0]),
        "x":             parse_int(r[1]),
        "y":             parse_int(r[2]),
        "tribe":         strip_quotes(r[3])  or "",
        "village_id":    parse_int(r[4]),
        "village_name":  strip_quotes(r[5])  or "",
        "player_id":     parse_int(r[6]),
        "player_name":   strip_quotes(r[7])  or "",
        "alliance_id":   parse_int(r[8]),
        "alliance_tag":  strip_quotes(r[9])  or "",
        "population":    parse_int(r[10]),
        "region":        strip_quotes(r[11]) or "",
        "capital":       parse_bool(r[12]),
        "city":          parse_bool(r[13]),
        "harbor":        parse_bool(r[14]),
        "victory_points":parse_int(r[15]),
        "dump_date":     ""
    }

def paginate(items: List[Any], page: int = 1, per_page: int = None) -> Dict[str, Any]:
    """Paginate a list of items."""
    if per_page is None:
        per_page = config.PAGE_SIZE
        
    start = (page - 1) * per_page
    end = start + per_page
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': total_items,
        'total_pages': total_pages,
        'has_next': end < total_items,
        'has_prev': start > 0
    }

# -------------------- Unified Data Getter -------------------- #
def get_all_villages() -> List[Dict[str,Any]]:
    """
    Get all villages from Supabase or SQL fallback.
    
    Tries to fetch from Supabase first, falls back to SQL dump if Supabase
    is unavailable. Uses caching to minimize network requests.
    
    Returns:
        List of village dictionaries
    """
    data: List[Dict[str,Any]] = []
    try:
        data = fetch_supabase_data()
        if data:
            logger.info(f"Loaded {len(data)} villages from Supabase")
            return data
        else:
            logger.warning("Supabase returned empty data")
    except Exception as e:
        logger.warning(f"Supabase fetch failed: {e}")

    # ⬇️ strictly local fallback (no network):
    if _cached_sql:
        rows = _cached_sql
        logger.info(f"Using cached SQL data: {len(rows)} rows")
    else:
        logger.info("Fetching SQL data (no cache available)")
        rows = fetch_sql_data()  # has its own short timeout & cache
        logger.info(f"Fetched {len(rows)} rows from SQL")
    
    result = [sql_row_to_dict(r) for r in rows]
    logger.info(f"Converted {len(result)} villages from SQL data")
    return result

# -------------------- Marker Rendering -------------------- #
_TRIBE_MAP = {1:"Romans",2:"Teutons",3:"Gauls",4:"Nature",
              5:"Natars",6:"Egyptians",7:"Huns",8:"Spartans",9:"Vikings"}

def get_color(idx:int)->str:
    """
    Generate a color for an index using HSL color space.
    
    Uses golden angle (137 degrees) for good color distribution.
    
    Args:
        idx: Color index
        
    Returns:
        HSL color string
    """
    return f"hsl({(idx*137)%360},70%,50%)"

def sanitize(s:str)->str:
    """
    Sanitize a string for use in CSS class names or IDs.
    
    Converts to lowercase, replaces non-alphanumeric with hyphens,
    and removes leading/trailing hyphens.
    
    Args:
        s: String to sanitize
        
    Returns:
        Sanitized string or "none" if empty
    """
    return re.sub(r"[^a-z0-9]+","-", s.lower()).strip("-") or "none"

def convert_y(y:int)->int:
    """
    Convert Y coordinate for SVG rendering (flip Y axis).
    
    Args:
        y: Original Y coordinate
        
    Returns:
        Negated Y coordinate
    """
    return -y

def generate_svg_markers(rows:List[Dict[str,Any]])->Dict[str,Any]:
    """
    Generate SVG markers and filter checkboxes from village data.
    
    Creates SVG rectangles for each village on the map, assigns colors by alliance,
    and generates filter checkboxes for alliances, regions, and tribes.
    
    Args:
        rows: List of village dictionaries
        
    Returns:
        Dictionary with markers SVG, checkboxes HTML, and region statistics JSON
    """
    faction_colors, alliance_map, region_map, tribe_map = {},{}, {},{}
    color_idx, region_stats, markers = 0, {}, []
    for r in rows:
        try:
            x = int(r["x"]); y = int(r["y"])
            alliance = r.get("alliance_tag","Natars") or "Natars"
            region   = r.get("region","") or ""
            # Handle tribe - it might be a string or int
            tribe_val = r.get("tribe") or 0
            if isinstance(tribe_val, str):
                # Try to convert string to int, fallback to 0
                try:
                    tid = int(tribe_val) if tribe_val.strip() else 0
                except (ValueError, AttributeError):
                    tid = 0
            else:
                tid = int(tribe_val) if tribe_val else 0
            tribe    = _TRIBE_MAP.get(tid,"Unknown")
            vname    = r.get("village_name","")
            pname    = r.get("player_name","")
            pop      = int(r.get("population") or 0)

            if alliance not in faction_colors:
                faction_colors[alliance] = get_color(color_idx); color_idx+=1
            color = faction_colors[alliance]

            sf, sr, st = sanitize(alliance), sanitize(region), sanitize(tribe)
            alliance_map[alliance], region_map[region], tribe_map[tribe] = sf, sr, st

            stats = region_stats.setdefault(region,{
                "villageCount":0, "totalPopulation":0,
                "largestVillage":"", "largestPopulation":0,
                "alliances": set()
            })
            stats["villageCount"]    += 1
            stats["totalPopulation"] += pop
            stats["alliances"].add(alliance)
            if pop > stats["largestPopulation"]:
                stats["largestPopulation"] = pop
                stats["largestVillage"]    = vname

            tip = (f"Village: {vname}<br>"
                   f"Player: {pname}<br>"
                   f"Population: {pop}<br>"
                   f"Alliance: {alliance}<br>"
                   f"Region: {region}<br>"
                   f"Tribe: {tribe}")
            markers.append(
                f'<rect class="marker alliance-{sf} region-{sr} tribe-{st}" '
                f'x="{x}" y="{convert_y(y)}" width="1" height="1" '
                f'fill="{color}" stroke="black" stroke-width="0.05" '
                f'data-tooltip="{tip}" data-player="{pname}" />'
            )
        except:
            continue

    for s in region_stats.values():
        s["allianceCount"] = len(s.pop("alliances"))

    alliance_cb = "\n".join(
        f'<div><input type="checkbox" class="alliance-checkbox" '
        f'id="toggleAlliance-{sf}" checked>'
        f'<label for="toggleAlliance-{sf}">{a}</label></div>'
        for a, sf in alliance_map.items()
    )
    region_cb = "\n".join(
        f'<div><input type="checkbox" class="region-checkbox" '
        f'id="toggleRegion-{sr}" checked>'
        f'<label for="toggleRegion-{sr}">{rnm}</label></div>'
        for rnm, sr in region_map.items() if rnm
    )
    tribe_cb = "\n".join(
        f'<div><input type="checkbox" class="tribe-checkbox" '
        f'id="toggleTribe-{st}" checked>'
        f'<label for="toggleTribe-{st}">{tnm}</label></div>'
        for tnm, st in tribe_map.items() if tnm.lower()!="unknown"
    )

    return {
        "markers":             "\n".join(markers),
        "alliance_checkboxes": alliance_cb,
        "region_checkboxes":   region_cb,
        "tribe_checkboxes":    tribe_cb,
        "region_stats_json":   json.dumps(region_stats)
    }

def _inject_common_fields(vs:List[Dict[str,Any]])->None:
    """
    Inject common computed fields into village dictionaries.
    
    Adds formatted coordinates, normalized field names, and tribe names
    to each village dictionary in place.
    
    Args:
        vs: List of village dictionaries to modify
    """
    for r in vs:
        try:   r["coords"] = f"({int(r['x'])},{int(r['y'])})"
        except: r["coords"] = "(0,0)"
        r["village"]       = r.get("village_name","")
        r["population"]    = int(r.get("population") or 0)
        r["victoryPoints"] = int(r.get("victory_points") or 0)
        r["alliance"]      = r.get("alliance_tag","")
        r["player"]        = r.get("player_name","")
        try:   tid = int(r.get("tribe") or 0)
        except: tid = 0
        r["tribe"]         = _TRIBE_MAP.get(tid,"Unknown")

# -------------------- Metrics Collection -------------------- #
class MetricsCollector:
    """Collect performance and usage metrics."""
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.endpoint_times: Dict[str, List[float]] = {}
        self.start_time = datetime.utcnow()
        self.redis_hits = 0
        self.redis_misses = 0
        self.supabase_queries = 0
        
    def record_request(self, endpoint: str, duration: float, is_error: bool = False):
        """Record a request metric."""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        if endpoint not in self.endpoint_times:
            self.endpoint_times[endpoint] = []
        self.endpoint_times[endpoint].append(duration)
        # Keep only last 1000 measurements per endpoint
        if len(self.endpoint_times[endpoint]) > 1000:
            self.endpoint_times[endpoint] = self.endpoint_times[endpoint][-1000:]
    
    def record_redis_hit(self):
        """Record a Redis cache hit."""
        self.redis_hits += 1
    
    def record_redis_miss(self):
        """Record a Redis cache miss."""
        self.redis_misses += 1
    
    def record_supabase_query(self):
        """Record a Supabase query."""
        self.supabase_queries += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        endpoint_stats = {}
        for endpoint, times in self.endpoint_times.items():
            if times:
                endpoint_stats[endpoint] = {
                    'count': len(times),
                    'avg_duration': sum(times) / len(times),
                    'min_duration': min(times),
                    'max_duration': max(times)
                }
        redis_total = self.redis_hits + self.redis_misses
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': self.error_count / self.request_count if self.request_count > 0 else 0,
            'uptime_seconds': uptime,
            'endpoints': endpoint_stats,
            'redis': {
                'hits': self.redis_hits,
                'misses': self.redis_misses,
                'hit_ratio': self.redis_hits / redis_total if redis_total > 0 else 0
            },
            'supabase_queries': self.supabase_queries
        }

metrics = MetricsCollector()

# -------------------- API Endpoints -------------------- #
@app.route("/api/ping")
@api_error_handler
def api_ping():
    """
    Simple ping endpoint to check if the API is running.
    
    Returns:
        JSON response with status and timestamp
    """
    return jsonify(success_response("pong", "API is running", 200)[0])

@app.route("/api/health")
@api_error_handler
def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
        JSON response with health status, cache stats, and metrics
    """
    redis_health = redis_health_check()
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'api': 'ok',
            'supabase': 'reachable' if supabase_reachable(1.0) else 'unreachable',
            'redis': redis_health,
            'cache': {
                'in_memory': {
                    'supabase': supabase_cache.stats(),
                    'sql': sql_cache.stats()
                },
                'redis': redis_health
            }
        },
        'metrics': metrics.get_stats()
    }
    return jsonify(health_data), 200

@app.route("/api/cache/clear", methods=["POST"])
@api_error_handler
def clear_cache():
    """
    Clear all caches (requires authentication in production).
    
    Returns:
        JSON response with cache statistics after clearing
    """
    supabase_cache.clear()
    sql_cache.clear()
    logger.info("Caches cleared by user request")
    return jsonify(success_response({
        'cache_stats': {
            'supabase': supabase_cache.stats(),
            'sql': sql_cache.stats()
        }
    }, "Caches cleared", 200)[0])

@app.route("/api/markers")
@api_error_handler
def api_markers():
    """
    Get map markers with optional filtering.
    
    Query Parameters:
        region (optional): Filter by region name
        alliance (optional): Filter by alliance tag
        player (optional): Filter by player name
        
    Returns:
        JSON response with SVG markers and filter checkboxes (raw format for frontend compatibility)
    """
    start_time = time.time()
    
    # Get latest dump_date for cache key
    dump_date = get_latest_dump_date()
    
    # Build cache key from filters
    region = request.args.get('region', '').strip()
    alliance = request.args.get('alliance', '').strip()
    player = request.args.get('player', '').strip()
    
    cache_key_parts = [f"markers:{dump_date}"]
    if region:
        region = validate_string_param(region, 'region')
        cache_key_parts.append(f"region={region}")
    if alliance:
        alliance = validate_string_param(alliance, 'alliance')
        cache_key_parts.append(f"alliance={alliance}")
    if player:
        player = validate_string_param(player, 'player')
        cache_key_parts.append(f"player={player}")
    
    cache_key = ":".join(cache_key_parts)
    
    # Try Redis cache first
    cached_data = cache_get_gzip_json(cache_key)
    if cached_data:
        metrics.record_redis_hit()
        logger.debug(f"Cache hit for markers: {cache_key}")
        duration = time.time() - start_time
        metrics.record_request('/api/markers', duration)
        return jsonify(cached_data)
    
    metrics.record_redis_miss()
    logger.info(f"Cache miss for markers: {cache_key}, querying Supabase")
    
    # Query Supabase with filters
    villages: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date)
            
            if region:
                query = query.eq("region", region)
            if alliance:
                query = query.eq("alliance_tag", alliance)
            if player:
                query = query.eq("player_name", player)
            
            # Paginate through results
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                villages.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
            
            logger.info(f"Fetched {len(villages)} villages from Supabase for markers")
        except Exception as e:
            logger.warning(f"Supabase query failed for markers: {e}, falling back to get_all_villages()")
            villages = get_all_villages()
    else:
        # Fallback to get_all_villages if Supabase unreachable
        villages = get_all_villages()
    
    # Apply filters if not already applied by Supabase query
    if not supabase_reachable(1.0) or not villages:
        if region:
            villages = [v for v in villages if v.get('region', '').lower() == region.lower()]
        if alliance:
            villages = [v for v in villages if (v.get('alliance_tag') or '').lower() == alliance.lower()]
        if player:
            villages = [v for v in villages if (v.get('player_name') or '').lower() == player.lower()]
    
    logger.info(f"After filtering: {len(villages)} villages")
    
    # Generate markers data
    markers_start = time.time()
    markers_data = generate_svg_markers(villages)
    markers_duration = time.time() - markers_start
    logger.info(f"Marker generation took {markers_duration:.2f}s for {len(villages)} villages")
    
    # Cache the result (use gzip for large payloads)
    # TTL: 3600 seconds or until next dump (whichever comes first)
    cache_set_gzip_json(cache_key, markers_data, ttl=3600)
    
    # Log if markers are empty
    if not markers_data.get("markers"):
        logger.warning(f"Generated markers are empty. Input villages: {len(villages)}")
        if villages:
            logger.info(f"Sample village structure: {list(villages[0].keys()) if villages else 'no villages'}")
    
    duration = time.time() - start_time
    metrics.record_request('/api/markers', duration)
    
    return jsonify(markers_data)

@app.route("/api/region", methods=["GET"])
@api_error_handler
def api_region_list():
    """
    Return a sorted list of every region present in the latest dataset.
    
    Returns:
        JSON response with list of unique region names
    """
    start_time = time.time()
    dump_date = get_latest_dump_date()
    cache_key = f"regions:{dump_date}"
    
    # Try Redis cache first
    cached_regions = cache_get_json(cache_key)
    if cached_regions:
        metrics.record_redis_hit()
        duration = time.time() - start_time
        metrics.record_request('/api/region', duration)
        return jsonify(cached_regions)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    villages: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("region").eq("dump_date", dump_date)
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                villages.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
        except Exception as e:
            logger.warning(f"Supabase query failed for regions: {e}, falling back")
            villages = get_all_villages()
    else:
        villages = get_all_villages()
    
    seen = set()
    for v in villages:
        reg = (v.get("region") or "").strip()
        if reg == "":
            reg = "None"
        seen.add(reg)

    regions = sorted(seen)
    
    # Cache the result
    cache_set_json(cache_key, regions, ttl=3600)
    
    duration = time.time() - start_time
    metrics.record_request('/api/region', duration)
    return jsonify(regions)

# ——— List all alliance tags (simple array) ———
@app.route("/api/alliance")
@api_error_handler
def api_alliance_tags():
    """
    Return a simple list of all alliance tags (strings).
    
    This endpoint is used by the frontend to get a list of alliance tags
    for iterating over and fetching detailed data for each alliance.
    
    Returns:
        JSON response with array of alliance tag strings
    """
    start_time = time.time()
    dump_date = get_latest_dump_date()
    cache_key = f"alliance_tags:{dump_date}"
    
    # Try Redis cache first
    cached_tags = cache_get_json(cache_key)
    if cached_tags:
        metrics.record_redis_hit()
        duration = time.time() - start_time
        metrics.record_request('/api/alliance', duration)
        return jsonify(cached_tags)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    villages: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("alliance_tag").eq("dump_date", dump_date)
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                villages.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
        except Exception as e:
            logger.warning(f"Supabase query failed for alliance tags: {e}, falling back")
            villages = get_all_villages()
    else:
        villages = get_all_villages()
    
    alliance_tags = set()
    for village in villages:
        alliance_tag = (village.get('alliance_tag') or '').strip()
        if not alliance_tag:
            alliance_tag = "Natars"
        alliance_tags.add(alliance_tag)
    
    sorted_tags = sorted(alliance_tags)
    
    # Cache the result
    cache_set_json(cache_key, sorted_tags, ttl=3600)
    
    duration = time.time() - start_time
    metrics.record_request('/api/alliance', duration)
    return jsonify(sorted_tags)

# ——— List all alliances ———
@app.route("/api/alliances")
@api_error_handler
def api_alliance_list():
    """Return a list of all alliances with their member counts."""
    start_time = time.time()
    dump_date = get_latest_dump_date()
    cache_key = f"alliances:{dump_date}"
    
    # Try Redis cache first
    cached_data = cache_get_json(cache_key)
    if cached_data:
        metrics.record_redis_hit()
        duration = time.time() - start_time
        metrics.record_request('/api/alliances', duration)
        return jsonify(cached_data)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    villages: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date)
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                villages.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
        except Exception as e:
            logger.warning(f"Supabase query failed for alliances: {e}, falling back")
            villages = get_all_villages()
    else:
        villages = get_all_villages()
    
    alliances = {}
    
    for village in villages:
        # Normalize alliance_tag: empty/None becomes "Natars" (consistent with other endpoints)
        alliance_tag = (village.get('alliance_tag') or '').strip()
        if not alliance_tag:
            alliance_tag = "Natars"
        
        # Initialize alliance if not seen before
        if alliance_tag not in alliances:
            alliances[alliance_tag] = {
                'tag': alliance_tag,
                'name': village.get('alliance_name', alliance_tag),  # Use tag as name if no name available
                'member_count': 0,
                'village_count': 0,
                'total_population': 0
            }
        
        # Update counts
        alliances[alliance_tag]['village_count'] += 1
        alliances[alliance_tag]['total_population'] += int(village.get('population', 0))
    
    # Count unique players per alliance
    players_by_alliance = {}
    for village in villages:
        alliance_tag = (village.get('alliance_tag') or '').strip()
        if not alliance_tag:
            alliance_tag = "Natars"
        player_id = village.get('player_id')
        
        if player_id:
            if alliance_tag not in players_by_alliance:
                players_by_alliance[alliance_tag] = set()
            players_by_alliance[alliance_tag].add(player_id)
    
    # Update member counts
    for alliance_tag, players in players_by_alliance.items():
        if alliance_tag in alliances:
            alliances[alliance_tag]['member_count'] = len(players)
    
    # Sort alliances by total population (descending)
    sorted_alliances = sorted(alliances.values(), key=lambda a: a['total_population'], reverse=True)
    
    result = {
        'alliances': sorted_alliances,
        'total': len(alliances)
    }
    
    # Cache the result
    cache_set_json(cache_key, result, ttl=3600)
    
    duration = time.time() - start_time
    metrics.record_request('/api/alliances', duration)
    
    return jsonify(result)

@app.route("/api/region/<region_name>/map")
@api_error_handler
def api_region_map(region_name):
    """
    Get map markers for a specific region.
    
    Args:
        region_name: Name of the region (use "None" for villages without a region)
        
    Returns:
        JSON response with SVG markers for the region (raw format for frontend compatibility)
    """
    start_time = time.time()
    region_name = validate_string_param(region_name, 'region_name')
    dump_date = get_latest_dump_date()
    cache_key = f"region_map:{dump_date}:{region_name}"
    
    # Try Redis cache first
    cached_data = cache_get_gzip_json(cache_key)
    if cached_data:
        metrics.record_redis_hit()
        duration = time.time() - start_time
        metrics.record_request('/api/region/<region_name>/map', duration)
        return jsonify(cached_data)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    rows: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date)
            
            # Handle "None" region specially - fetch all and filter in Python
            if region_name.lower() != "none":
                query = query.eq("region", region_name)
            
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                rows.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
            
            # Filter for "None" region in Python if needed
            if region_name.lower() == "none":
                rows = [r for r in rows if not (r.get("region") or "").strip()]
        except Exception as e:
            logger.warning(f"Supabase query failed for region map: {e}, falling back")
            rows = get_all_villages()
            # Handle "None" region specially - match empty/whitespace regions
            if region_name.lower() == "none":
                rows = [r for r in rows if not (r.get("region") or "").strip()]
            else:
                rows = [r for r in rows if (r.get("region") or "").strip().lower() == region_name.lower()]
    else:
        rows = get_all_villages()
        # Handle "None" region specially - match empty/whitespace regions
        if region_name.lower() == "none":
            rows = [r for r in rows if not (r.get("region") or "").strip()]
        else:
            rows = [r for r in rows if (r.get("region") or "").strip().lower() == region_name.lower()]
    
    if not rows:
        raise APIError(f"No data found for region: {region_name}", 404)
    
    markers_data = generate_svg_markers(rows)
    
    # Cache the result
    cache_set_gzip_json(cache_key, markers_data, ttl=3600)
    
    duration = time.time() - start_time
    metrics.record_request('/api/region/<region_name>/map', duration)
    return jsonify(markers_data)

@app.route("/api/region/<region_name>/villages")
@api_error_handler
def api_region_villages(region_name):
    """
    Get all villages in a specific region with optional pagination.
    
    Args:
        region_name: Name of the region (use "None" for villages without a region)
        
    Query Parameters:
        page (optional): Page number (default: 1) - if provided, returns paginated format
        per_page (optional): Items per page (default: 1000, max: 1000)
        
    Returns:
        JSON response with list of villages (backward compatible format by default)
    """
    start_time = time.time()
    region_name = validate_string_param(region_name, 'region_name')
    dump_date = get_latest_dump_date()
    
    # Check pagination params
    has_page = request.args.get('page') is not None
    has_per_page = request.args.get('per_page') is not None
    page = request.args.get('page', 1, type=int) if has_page else 1
    per_page = request.args.get('per_page', 1000, type=int) if has_per_page else 1000
    
    # Build cache key
    cache_key = f"region_villages:{dump_date}:{region_name}"
    if has_page or has_per_page:
        cache_key += f":page={page}:per_page={per_page}"
    
    # Try Redis cache first (only for non-paginated or first page)
    if not (has_page and page > 1):
        cached_data = cache_get_json(cache_key)
        if cached_data:
            metrics.record_redis_hit()
            duration = time.time() - start_time
            metrics.record_request('/api/region/<region_name>/villages', duration)
            return jsonify(cached_data)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    rows: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date)
            
            # Handle "None" region specially - fetch all and filter in Python
            if region_name.lower() != "none":
                query = query.eq("region", region_name)
            
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                rows.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
            
            # Filter for "None" region in Python if needed
            if region_name.lower() == "none":
                rows = [r for r in rows if not (r.get("region") or "").strip()]
        except Exception as e:
            logger.warning(f"Supabase query failed for region villages: {e}, falling back")
            rows = get_all_villages()
            # Handle "None" region specially - match empty/whitespace regions
            if region_name.lower() == "none":
                rows = [r for r in rows if not (r.get("region") or "").strip()]
            else:
                rows = [r for r in rows if (r.get("region") or "").strip().lower() == region_name.lower()]
    else:
        rows = get_all_villages()
        # Handle "None" region specially - match empty/whitespace regions
        if region_name.lower() == "none":
            rows = [r for r in rows if not (r.get("region") or "").strip()]
        else:
            rows = [r for r in rows if (r.get("region") or "").strip().lower() == region_name.lower()]
    
    if not rows:
        raise APIError(f"No data for region {region_name}", 404)
    
    _inject_common_fields(rows)
    
    # If pagination is explicitly requested, use new format
    if has_page or has_per_page:
        page, per_page = validate_pagination_params(page, per_page, max_per_page=1000)
        result = paginate(rows, page, per_page)
        
        response_data = success_response({
            'region': region_name,
            'villages': result['items'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'total_pages': result['total_pages'],
                'has_next': result['has_next'],
                'has_prev': result['has_prev']
            }
        }, f"Villages for region {region_name} retrieved")[0]
        
        # Cache only first page
        if page == 1:
            cache_set_json(cache_key, response_data, ttl=3600)
        
        duration = time.time() - start_time
        metrics.record_request('/api/region/<region_name>/villages', duration)
        return jsonify(response_data)
    
    # Otherwise, return backward compatible format (old format)
    response_data = {'region': region_name, 'villages': rows}
    
    # Cache the result
    cache_set_json(cache_key, response_data, ttl=3600)
    
    duration = time.time() - start_time
    metrics.record_request('/api/region/<region_name>/villages', duration)
    return jsonify(response_data)

@app.route("/api/alliance/<alliance_tag>/map")
@api_error_handler
def api_alliance_map(alliance_tag):
    """
    Get map markers for a specific alliance.
    
    Args:
        alliance_tag: Tag of the alliance (use "Natars" for villages without alliance)
        
    Returns:
        JSON response with SVG markers for the alliance (raw format for frontend compatibility)
    """
    start_time = time.time()
    alliance_tag = validate_string_param(alliance_tag, 'alliance_tag')
    lower = alliance_tag.lower()
    dump_date = get_latest_dump_date()
    cache_key = f"alliance_map:{dump_date}:{alliance_tag}"
    
    # Try Redis cache first
    cached_data = cache_get_gzip_json(cache_key)
    if cached_data:
        metrics.record_redis_hit()
        duration = time.time() - start_time
        metrics.record_request('/api/alliance/<alliance_tag>/map', duration)
        return jsonify(cached_data)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    rows: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date)
            
            # Handle "Natars" specially - fetch all and filter in Python
            if lower != "natars":
                query = query.eq("alliance_tag", alliance_tag)
            
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                rows.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
            
            # Filter for "Natars" in Python if needed
            if lower == "natars":
                rows = [r for r in rows if not (r.get("alliance_tag") or "").strip()]
        except Exception as e:
            logger.warning(f"Supabase query failed for alliance map: {e}, falling back")
            rows = get_all_villages()
            if lower == "natars":
                rows = [r for r in rows if not (r.get("alliance_tag") or "").strip()]
            else:
                rows = [r for r in rows if (r.get("alliance_tag") or "").strip().lower() == lower]
    else:
        rows = get_all_villages()
        if lower == "natars":
            rows = [r for r in rows if not (r.get("alliance_tag") or "").strip()]
        else:
            rows = [r for r in rows if (r.get("alliance_tag") or "").strip().lower() == lower]
    
    if not rows:
        raise APIError(f"No data found for alliance: {alliance_tag}", 404)
    
    markers_data = generate_svg_markers(rows)
    
    # Cache the result
    cache_set_gzip_json(cache_key, markers_data, ttl=3600)
    
    duration = time.time() - start_time
    metrics.record_request('/api/alliance/<alliance_tag>/map', duration)
    return jsonify(markers_data)

@app.route("/api/alliance/<alliance_tag>/villages")
@api_error_handler
def api_alliance_villages(alliance_tag):
    """
    Get all villages for a specific alliance with optional pagination.
    
    Args:
        alliance_tag: Tag of the alliance (use "Natars" for villages without alliance)
        
    Query Parameters:
        page (optional): Page number (default: 1) - if provided, returns paginated format
        per_page (optional): Items per page (default: 1000, max: 1000)
        
    Returns:
        JSON response with list of villages (backward compatible format by default)
    """
    start_time = time.time()
    alliance_tag = validate_string_param(alliance_tag, 'alliance_tag')
    lower = alliance_tag.lower()
    dump_date = get_latest_dump_date()
    
    # Check pagination params
    has_page = request.args.get('page') is not None
    has_per_page = request.args.get('per_page') is not None
    page = request.args.get('page', 1, type=int) if has_page else 1
    per_page = request.args.get('per_page', 1000, type=int) if has_per_page else 1000
    
    # Build cache key
    cache_key = f"alliance_villages:{dump_date}:{alliance_tag}"
    if has_page or has_per_page:
        cache_key += f":page={page}:per_page={per_page}"
    
    # Try Redis cache first (only for non-paginated or first page)
    if not (has_page and page > 1):
        cached_data = cache_get_json(cache_key)
        if cached_data:
            metrics.record_redis_hit()
            duration = time.time() - start_time
            metrics.record_request('/api/alliance/<alliance_tag>/villages', duration)
            return jsonify(cached_data)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    rows: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date)
            
            # Handle "Natars" specially - fetch all and filter in Python
            if lower != "natars":
                query = query.eq("alliance_tag", alliance_tag)
            
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                rows.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
            
            # Filter for "Natars" in Python if needed
            if lower == "natars":
                rows = [r for r in rows if not (r.get("alliance_tag") or "").strip()]
        except Exception as e:
            logger.warning(f"Supabase query failed for alliance villages: {e}, falling back")
            rows = get_all_villages()
            if lower == "natars":
                rows = [r for r in rows if not (r.get("alliance_tag") or "").strip()]
            else:
                rows = [r for r in rows if (r.get("alliance_tag") or "").strip().lower() == lower]
    else:
        rows = get_all_villages()
        if lower == "natars":
            rows = [r for r in rows if not (r.get("alliance_tag") or "").strip()]
        else:
            rows = [r for r in rows if (r.get("alliance_tag") or "").strip().lower() == lower]
    
    # Return empty array instead of error - frontend can handle empty results
    _inject_common_fields(rows)
    
    # If pagination is explicitly requested, use new format
    if has_page or has_per_page:
        page, per_page = validate_pagination_params(page, per_page, max_per_page=1000)
        result = paginate(rows, page, per_page)
        
        response_data = success_response({
            'alliance': alliance_tag,
            'villages': result['items'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'total_pages': result['total_pages'],
                'has_next': result['has_next'],
                'has_prev': result['has_prev']
            }
        }, f"Villages for alliance {alliance_tag} retrieved")[0]
        
        # Cache only first page
        if page == 1:
            cache_set_json(cache_key, response_data, ttl=3600)
        
        duration = time.time() - start_time
        metrics.record_request('/api/alliance/<alliance_tag>/villages', duration)
        return jsonify(response_data)
    
    # Otherwise, return backward compatible format (old format)
    response_data = {'alliance': alliance_tag, 'villages': rows}
    
    # Cache the result
    cache_set_json(cache_key, response_data, ttl=3600)
    
    duration = time.time() - start_time
    metrics.record_request('/api/alliance/<alliance_tag>/villages', duration)
    return jsonify(response_data)

@app.route("/api/player/<player_name>/map")
@api_error_handler
def api_player_map(player_name):
    """
    Get map markers for a specific player.
    
    Args:
        player_name: Name of the player
        
    Returns:
        JSON response with SVG markers for the player (raw format for frontend compatibility)
    """
    start_time = time.time()
    player_name = validate_string_param(player_name, 'player_name')
    dump_date = get_latest_dump_date()
    cache_key = f"player_map:{dump_date}:{player_name}"
    
    # Try Redis cache first
    cached_data = cache_get_gzip_json(cache_key)
    if cached_data:
        metrics.record_redis_hit()
        duration = time.time() - start_time
        metrics.record_request('/api/player/<player_name>/map', duration)
        return jsonify(cached_data)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    rows: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date).eq("player_name", player_name)
            
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                rows.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
        except Exception as e:
            logger.warning(f"Supabase query failed for player map: {e}, falling back")
            rows = get_all_villages()
            rows = [r for r in rows if r.get("player_name","").lower() == player_name.lower()]
    else:
        rows = get_all_villages()
        rows = [r for r in rows if r.get("player_name","").lower() == player_name.lower()]
    
    if not rows:
        raise APIError(f"No data found for player: {player_name}", 404)
    
    markers_data = generate_svg_markers(rows)
    
    # Cache the result (shorter TTL for player-specific data)
    cache_set_gzip_json(cache_key, markers_data, ttl=1800)
    
    duration = time.time() - start_time
    metrics.record_request('/api/player/<player_name>/map', duration)
    return jsonify(markers_data)

@app.route("/api/player/<player_name>/villages")
@api_error_handler
def api_player_villages(player_name):
    """
    Get all villages for a specific player with optional pagination.
    
    Args:
        player_name: Name of the player
        
    Query Parameters:
        page (optional): Page number (default: 1) - if provided, returns paginated format
        per_page (optional): Items per page (default: 1000, max: 1000)
        
    Returns:
        JSON response with list of villages (backward compatible format by default)
    """
    start_time = time.time()
    player_name = validate_string_param(player_name, 'player_name')
    dump_date = get_latest_dump_date()
    
    # Check pagination params
    has_page = request.args.get('page') is not None
    has_per_page = request.args.get('per_page') is not None
    page = request.args.get('page', 1, type=int) if has_page else 1
    per_page = request.args.get('per_page', 1000, type=int) if has_per_page else 1000
    
    # Build cache key
    cache_key = f"player_villages:{dump_date}:{player_name}"
    if has_page or has_per_page:
        cache_key += f":page={page}:per_page={per_page}"
    
    # Try Redis cache first (only for non-paginated or first page)
    if not (has_page and page > 1):
        cached_data = cache_get_json(cache_key)
        if cached_data:
            metrics.record_redis_hit()
            duration = time.time() - start_time
            metrics.record_request('/api/player/<player_name>/villages', duration)
            return jsonify(cached_data)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    vs: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date).eq("player_name", player_name)
            
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                vs.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
        except Exception as e:
            logger.warning(f"Supabase query failed for player villages: {e}, falling back")
            vs = [r for r in get_all_villages() if r.get("player_name","").lower() == player_name.lower()]
    else:
        vs = [r for r in get_all_villages() if r.get("player_name","").lower() == player_name.lower()]
    
    if not vs:
        raise APIError(f"No data for player {player_name}", 404)
    
    _inject_common_fields(vs)
    
    # If pagination is explicitly requested, use new format
    if has_page or has_per_page:
        page, per_page = validate_pagination_params(page, per_page, max_per_page=1000)
        result = paginate(vs, page, per_page)
        
        response_data = success_response({
            'player': player_name,
            'villages': result['items'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'total_pages': result['total_pages'],
                'has_next': result['has_next'],
                'has_prev': result['has_prev']
            }
        }, f"Villages for player {player_name} retrieved")[0]
        
        # Cache only first page (shorter TTL for player-specific data)
        if page == 1:
            cache_set_json(cache_key, response_data, ttl=1800)
        
        duration = time.time() - start_time
        metrics.record_request('/api/player/<player_name>/villages', duration)
        return jsonify(response_data)
    
    # Otherwise, return backward compatible format (old format)
    response_data = {'player': player_name, 'villages': vs}
    
    # Cache the result (shorter TTL for player-specific data)
    cache_set_json(cache_key, response_data, ttl=1800)
    
    duration = time.time() - start_time
    metrics.record_request('/api/player/<player_name>/villages', duration)
    return jsonify(response_data)

@app.route("/api/player/<player_name>/history")
@api_error_handler
def api_player_history(player_name: str):
    """
    Return time-series for a player's total villages & population per dump_date.
    If Supabase is unreachable or errors, degrade gracefully without touching the network.
    
    Args:
        player_name: Name of the player
        
    Returns:
        JSON response with historical data (villages and population over time)
    """
    start_time = time.time()
    player_name = validate_string_param(player_name, 'player_name')
    # Try Supabase only if reachable
    if supabase_reachable(1.0):
        try:
            resp = (supabase.table("villages")
                            .select("dump_date,population,player_name")
                            .ilike("player_name", player_name)
                            .execute())
            vs = resp.data or []
            stats: Dict[str, Dict[str, int]] = {}
            for r in vs:
                d = r["dump_date"]
                stats.setdefault(d, {"villages": 0, "population": 0})
                stats[d]["villages"] += 1
                stats[d]["population"] += int(r.get("population") or 0)
            history = [{"date": d,
                        "villages": stats[d]["villages"],
                        "population": stats[d]["population"]}
                       for d in sorted(stats)]
            duration = time.time() - start_time
            metrics.record_request('/api/player/<player_name>/history', duration)
            return jsonify(success_response({
                'player': player_name,
                'history': history
            }, "Player history retrieved successfully")[0])
        except Exception as e:
            logger.error("Supabase history lookup failed for %s: %s", player_name, e)

    # ⬇️ LOCAL, non-network fallback — use in-memory caches only
    player_lower = player_name.lower()
    rows: List[Dict[str, Any]] = []

    if _cached_rows:
        rows = _cached_rows
    elif _cached_sql:
        rows = [sql_row_to_dict(r) for r in _cached_sql]
    else:
        # last resort; may try network but has short timeout & cache
        rows = [sql_row_to_dict(r) for r in fetch_sql_data()]

    rows = [r for r in rows if (r.get("player_name") or "").lower() == player_lower]
    if rows:
        total_pop = sum(int(r.get("population") or 0) for r in rows)
        today = date.today().isoformat()
        history = [{"date": today, "villages": len(rows), "population": total_pop}]
    else:
        history = []

    duration = time.time() - start_time
    metrics.record_request('/api/player/<player_name>/history', duration)
    return jsonify(success_response({
        'player': player_name,
        'history': history
    }, "Player history retrieved successfully")[0])


@app.route("/api/players")
@api_error_handler
def api_players():
    """
    Get list of all players sorted by population with pagination.
    
    Query Parameters:
        limit (optional): Maximum number of players to return (default: 300, max: 1000)
        page (optional): Page number (default: 1)
        per_page (optional): Items per page (default: 300, max: 1000)
        
    Returns:
        JSON response with paginated list of players sorted by population
    """
    start_time = time.time()
    dump_date = get_latest_dump_date()
    
    # Check pagination params
    has_page = request.args.get('page') is not None
    has_per_page = request.args.get('per_page') is not None
    limit = request.args.get("limit", type=int)
    page = request.args.get('page', 1, type=int) if has_page else 1
    per_page = request.args.get('per_page', 300, type=int) if has_per_page else 300
    
    # Build cache key
    cache_key = f"players:{dump_date}"
    if has_page or has_per_page:
        cache_key += f":page={page}:per_page={per_page}"
    elif limit:
        cache_key += f":limit={limit}"
    
    # Try Redis cache first (only for non-paginated or first page)
    if not (has_page and page > 1):
        cached_data = cache_get_json(cache_key)
        if cached_data:
            metrics.record_redis_hit()
            duration = time.time() - start_time
            metrics.record_request('/api/players', duration)
            return jsonify(cached_data)
    
    metrics.record_redis_miss()
    
    # Query Supabase
    rows: List[Dict[str, Any]] = []
    if supabase_reachable(1.0):
        try:
            metrics.record_supabase_query()
            query = supabase.table("villages").select("*").eq("dump_date", dump_date)
            page_size, offset = 1000, 0
            while True:
                chunk = query.range(offset, offset + page_size - 1).execute().data or []
                rows.extend(chunk)
                if len(chunk) < page_size:
                    break
                offset += page_size
        except Exception as e:
            logger.warning(f"Supabase query failed for players: {e}, falling back")
            rows = get_all_villages()
    else:
        rows = get_all_villages()
    
    players: Dict[str,Dict[str,Any]] = {}
    for r in rows:
        nm = (r.get("player_name") or "").strip()
        if not nm: continue
        alliance = r.get("alliance_tag","") or ""
        pop      = int(r.get("population") or 0)
        if nm not in players:
            players[nm] = {
                "id":int(r.get("player_id") or 0),
                "name":nm,
                "alliance":alliance,
                "villages":0,
                "population":0
            }
        players[nm]["villages"]  += 1
        players[nm]["population"]+= pop

    # If pagination is explicitly requested, use new format
    if has_page or has_per_page:
        page, per_page = validate_pagination_params(page, per_page, max_per_page=1000)
        
        sorted_players = sorted(players.values(), key=lambda p: p["population"], reverse=True)
        result = paginate(sorted_players, page, per_page)
        response_data = paginated_response(result['items'], result['page'], result['per_page'], result['total'])
        
        # Cache only first page
        if page == 1:
            cache_set_json(cache_key, response_data, ttl=3600)
        
        duration = time.time() - start_time
        metrics.record_request('/api/players', duration)
        return jsonify(response_data)
    
    # Otherwise, return array directly for backward compatibility
    if limit:
        limit = min(limit, 1000)
    else:
        limit = 300  # Default limit
    
    sorted_players = sorted(players.values(), key=lambda p: p["population"], reverse=True)
    top = sorted_players[:limit]
    
    # Cache the result
    cache_set_json(cache_key, top, ttl=3600)
    
    duration = time.time() - start_time
    metrics.record_request('/api/players', duration)
    return jsonify(top)

# -------------------- Ingest SQL → Supabase -------------------- #
def ingest_to_supabase():
    """
    Ingest SQL dump data into Supabase database.
    
    Fetches SQL data, converts to dictionaries, and upserts into Supabase
    villages table. Uses conflict resolution on village_id and dump_date.
    Invalidates Redis cache for latest_dump_date to trigger cache refresh.
    """
    rows = fetch_sql_data()
    today = date.today().isoformat()
    payload = [{**sql_row_to_dict(r), "dump_date": today} for r in rows]

    if not payload:
        logger.info("No rows to ingest")
        return

    try:
        res = (supabase.table("villages")
                        .upsert(payload, on_conflict="village_id,dump_date")
                        .execute())
        code = getattr(res, "status_code", None)
        if code in (200,201):
            logger.info("Ingested %d rows for %s", len(payload), today)
            
            # Invalidate latest_dump_date cache to force refresh
            cache_delete("latest_dump_date")
            logger.info("Invalidated latest_dump_date cache after ingestion")
        else:
            logger.error("Upsert failed: %s", res)
    except Exception as e:
        logger.error("Supabase upsert failed: %s", e)

@app.route("/")
def home():
    """Redirect root path to ping endpoint."""
    return redirect(url_for("api_ping"))

# -------------------- Main Application -------------------- #
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TraviStat Web Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--ingest', action='store_true', help='Run data ingestion before starting server')
    
    args = parser.parse_args()
    
    if args.ingest:
        logger.info("Starting data ingestion...")
        try:
            ingest_to_supabase()
            logger.info("Data ingestion completed successfully")
        except Exception as e:
            logger.error("Data ingestion failed: %s", str(e), exc_info=True)
    
    logger.info("Starting web server on %s:%d (debug=%s)", args.host, args.port, args.debug)
    app.run(host=args.host, port=args.port, debug=args.debug)
