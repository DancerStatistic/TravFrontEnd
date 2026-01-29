"""Authentication and authorization utilities."""
import logging
from functools import wraps
from typing import Optional, Callable
from flask import request, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

logger = logging.getLogger("bot")


class User(UserMixin):
    """User model for Flask-Login."""
    
    def __init__(self, id: str) -> None:
        self.id = id


def setup_auth(app, config) -> LoginManager:
    """Set up Flask-Login authentication."""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.session_protection = "strong"
    
    @login_manager.user_loader
    def load_user(uid: str) -> Optional[User]:
        """Load user from session."""
        if uid in config.AUTH_USERS:
            return User(uid)
        return None
    
    return login_manager


def login_route_handler(config):
    """Handle login POST request."""
    if not request.is_json:
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400
    
    if email in config.AUTH_USERS:
        user_data = config.AUTH_USERS[email]
        if user_data.get("password") == password:
            user = User(email)
            login_user(user, remember=True)
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "user": {"email": email}
            }), 200
    
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


def logout_route_handler():
    """Handle logout POST request."""
    logout_user()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200


def optional_auth(f: Callable) -> Callable:
    """
    Decorator for endpoints that work with or without authentication.
    
    If authentication is configured and user is logged in, current_user is available.
    If not authenticated, endpoint still works but may have limited functionality.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def require_auth(f: Callable) -> Callable:
    """
    Decorator to require authentication for an endpoint.
    
    Returns 401 if user is not authenticated.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function
