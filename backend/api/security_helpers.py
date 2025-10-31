"""
API Security Helpers
Provides security utilities for API endpoints including rate limiting,
authentication, and input validation.
"""

import os
import time
import hashlib
from typing import Optional, Callable
from functools import wraps
from collections import defaultdict
from fastapi import HTTPException, Header, Request
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter for API endpoints"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if client is allowed to make a request
        
        Args:
            client_id: Unique identifier for the client (IP, API key, etc.)
        
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Record new request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]
        return max(0, self.max_requests - len(self.requests[client_id]))


class APIKeyValidator:
    """Validates API keys for authentication"""
    
    def __init__(self):
        # In production, load from secure storage or environment
        self.api_key = os.environ.get("OVERSEER_API_KEY")
        self.require_auth = os.environ.get("OVERSEER_REQUIRE_AUTH", "false").lower() == "true"
    
    def validate_key(self, api_key: Optional[str]) -> bool:
        """
        Validate API key
        
        Args:
            api_key: API key to validate
        
        Returns:
            True if valid or auth not required, False otherwise
        """
        if not self.require_auth:
            return True
        
        if not self.api_key:
            logger.warning("OVERSEER_API_KEY not set but auth is required")
            return False
        
        if not api_key:
            return False
        
        # Constant-time comparison to prevent timing attacks
        return self._constant_time_compare(api_key, self.api_key)
    
    def _constant_time_compare(self, a: str, b: str) -> bool:
        """Constant-time string comparison to prevent timing attacks"""
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        
        return result == 0


class InputValidator:
    """Validates and sanitizes user input"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal
        
        Args:
            filename: Filename to sanitize
        
        Returns:
            Sanitized filename
        """
        # Remove path separators and null bytes
        sanitized = filename.replace('/', '').replace('\\', '').replace('\x00', '')
        
        # Remove parent directory references
        sanitized = sanitized.replace('..', '')
        
        return sanitized
    
    @staticmethod
    def sanitize_path(path: str, allowed_base: str) -> Optional[str]:
        """
        Sanitize and validate path to prevent traversal attacks
        
        Args:
            path: Path to sanitize
            allowed_base: Base directory that path must be within
        
        Returns:
            Sanitized absolute path if valid, None otherwise
        """
        import os
        
        # Resolve to absolute paths
        base = os.path.abspath(allowed_base)
        target = os.path.abspath(os.path.join(base, path))
        
        # Ensure target is within base
        if not target.startswith(base):
            return None
        
        return target
    
    @staticmethod
    def validate_input_length(input_str: str, max_length: int = 1000) -> bool:
        """
        Validate input length to prevent DoS
        
        Args:
            input_str: Input string to validate
            max_length: Maximum allowed length
        
        Returns:
            True if valid, False otherwise
        """
        return len(input_str) <= max_length
    
    @staticmethod
    def sanitize_sql_input(input_str: str) -> str:
        """
        Basic sanitization for SQL input (use parameterized queries instead!)
        
        Args:
            input_str: Input to sanitize
        
        Returns:
            Sanitized string
        """
        # Remove common SQL injection patterns
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        sanitized = input_str
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized


# Dependency injection for FastAPI
async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    FastAPI dependency for API key verification
    
    Args:
        x_api_key: API key from request header
    
    Returns:
        API key if valid
    
    Raises:
        HTTPException: If API key is invalid
    """
    validator = APIKeyValidator()
    
    if not validator.validate_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return x_api_key


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Decorator for rate limiting endpoints
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
    """
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Use IP address as client identifier
            client_ip = request.client.host
            
            if not limiter.is_allowed(client_ip):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + window_seconds)
                    }
                )
            
            # Add rate limit headers
            remaining = limiter.get_remaining(client_ip)
            response = await func(request, *args, **kwargs)
            
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
            
            return response
        
        return wrapper
    
    return decorator


# Security headers middleware
def add_security_headers(response):
    """Add security headers to response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
