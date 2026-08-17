"""Rate limiting middleware for API Gateway."""

import time
import os
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60, max_clients: int = 10000):
        self.requests_per_minute = requests_per_minute
        self.max_clients = max_clients
        self.requests: Dict[str, list[float]] = defaultdict(list)

    def _cleanup(self) -> None:
        """Remove stale client entries to prevent unbounded growth."""
        if len(self.requests) <= self.max_clients:
            return

        now = time.time()
        # Keep only entries with recent activity
        for client_id in list(self.requests.keys()):
            recent = [t for t in self.requests[client_id] if t > now - 60]
            if recent:
                self.requests[client_id] = recent
            else:
                del self.requests[client_id]

    def is_allowed(self, client_id: str) -> Tuple[bool, Dict]:
        """Check if request is allowed for client."""
        self._cleanup()
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

# Comma-separated list of trusted proxy IPs (empty = no proxy trust)
TRUSTED_PROXIES = {
    proxy.strip()
    for proxy in os.getenv("TRUSTED_PROXIES", "").split(",")
    if proxy.strip()
}


def get_client_ip(request: Request) -> str:
    """Get the real client IP, honoring X-Forwarded-For from trusted proxies."""
    if TRUSTED_PROXIES:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # X-Forwarded-For format: "client, proxy1, proxy2"
            return forwarded.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = get_client_ip(request)

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
