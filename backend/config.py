"""Configuration management for the backend application."""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:

    """Application configuration loaded from environment variables."""
    
    # Flask Configuration
    FLASK_SECRET: str = os.getenv("FLASK_SECRET", "dev-secret-change-in-production")
    PERMANENT_SESSION_LIFETIME: int = int(os.getenv("PERMANENT_SESSION_LIFETIME", "3600"))  # 1 hour
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")
    )
    
    # Supabase Configuration
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    SQL_CACHE_TTL: int = int(os.getenv("SQL_CACHE_TTL", "86400"))  # 24 hours
    PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", "1000"))  # Default page size
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    REDIS_PREFIX: str = os.getenv("REDIS_PREFIX", "travistat:")
    REDIS_DEFAULT_TTL_SECONDS: int = int(os.getenv("REDIS_DEFAULT_TTL_SECONDS", "3600"))  # 1 hour
    
    # Map Configuration
    SQL_FILE_URL: str = "https://nys.x1.europe.travian.com//map.sql"
    
    # Authentication Configuration
    # Users should be configured via environment variables in format:
    # AUTH_USERS=user1@example.com:password1,user2@example.com:password2
    # Or use a separate user management system
    AUTH_USERS: dict[str, dict[str, str]] = field(default_factory=dict)
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "1000 per hour")
    RATE_LIMIT_STRICT: str = os.getenv("RATE_LIMIT_STRICT", "100 per hour")  # For expensive endpoints
    
    def __post_init__(self):
        """Load users from environment variable after initialization."""
        # Default users (not recommended for production)
        # These are used if AUTH_USERS env var is not set
        default_users = {
            "admin@example.com": {"password": "your-secure-password"},
            # Add more users as needed
        }
        
        # Override with environment variable if set
        auth_users_env = os.getenv("AUTH_USERS", "").strip()
        if auth_users_env:
            # Parse format: user1@example.com:password1,user2@example.com:password2
            self.AUTH_USERS = {}
            for user_entry in auth_users_env.split(","):
                user_entry = user_entry.strip()
                if ":" in user_entry:
                    email, password = user_entry.split(":", 1)
                    self.AUTH_USERS[email.strip()] = {"password": password.strip()}
        else:
            # Use defaults if no env var
            self.AUTH_USERS = default_users.copy()
    
    def validate(self) -> None:
        """Validate required configuration values."""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY environment variable is required")
        # Redis is optional - will fallback to in-memory cache if not configured
        # Authentication users are optional - endpoints can be public if not configured
