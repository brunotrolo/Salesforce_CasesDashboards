"""Rate limiting middleware for API Gateway."""

import time
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> Tuple[bool, Dict]:
        """Check if request is allowed for client."""
        now = time.time()
        minute_ago = now - 60

        # Remove old requests
        self.requests[client_id] = [
            timestamp for timestamp in self.requests[client_id]
            if timestamp > minute_ago
        ]

        current_count = len(self.requests[client_id])

        if current_count >= self.requests_per_minute:
            return False, {
                "limit": self.requests_per_minute,
                "current": current_count,
                "reset_at": min(self.requests[client_id]) + 60
            }

        self.requests[client_id].append(now)
        return True, {
            "limit": self.requests_per_minute,
            "remaining": self.requests_per_minute - current_count - 1,
            "reset_at": now + 60
        }


# Global rate limiter: 100 requests per minute per IP
rate_limiter = RateLimiter(requests_per_minute=100)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        allowed, info = rate_limiter.is_allowed(client_ip)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(info["reset_at"]))
                }
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(int(info["reset_at"]))

        return response
