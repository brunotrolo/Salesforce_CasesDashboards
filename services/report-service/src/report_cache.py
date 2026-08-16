import json
import hashlib
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from .models.report import Report, ReportExecutionResult


class ReportCache:
    """In-memory cache for report execution results (Redis adapter)."""

    def __init__(self, ttl_minutes: int = 60):
        self.ttl_minutes = ttl_minutes
        self.cache: Dict[str, tuple[Any, datetime]] = {}

    def get_cache_key(self, report_id: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from report ID and filters."""
        key_parts = [report_id]

        if filters:
            # Sort filters for consistent hashing
            sorted_filters = json.dumps(filters, sort_keys=True)
            key_hash = hashlib.md5(sorted_filters.encode()).hexdigest()
            key_parts.append(key_hash)

        return ":".join(key_parts)

    def set(self, key: str, value: Any, ttl_minutes: Optional[int] = None) -> None:
        """Set cache entry with optional custom TTL."""
        ttl = ttl_minutes or self.ttl_minutes
        expiration = datetime.utcnow() + timedelta(minutes=ttl)
        self.cache[key] = (value, expiration)

    def get(self, key: str) -> Optional[Any]:
        """Get cache entry if not expired."""
        if key not in self.cache:
            return None

        value, expiration = self.cache[key]

        if datetime.utcnow() > expiration:
            del self.cache[key]
            return None

        return value

    def cache_result(
        self,
        report_id: str,
        result: ReportExecutionResult,
        filters: Optional[Dict[str, Any]] = None,
        ttl_minutes: Optional[int] = None,
    ) -> None:
        """Cache a report execution result."""
        key = self.get_cache_key(report_id, filters)
        self.set(key, result, ttl_minutes)

    def get_cached_result(
        self,
        report_id: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Optional[ReportExecutionResult]:
        """Retrieve cached report result."""
        key = self.get_cache_key(report_id, filters)
        return self.get(key)

    def invalidate_report(self, report_id: str) -> int:
        """Invalidate all cache entries for a report."""
        keys_to_delete = [k for k in self.cache.keys() if k.startswith(f"{report_id}") and (k == report_id or k.startswith(f"{report_id}:"))]
        count = len(keys_to_delete)

        for key in keys_to_delete:
            del self.cache[key]

        return count

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        expired_keys = [
            k for k, (_, exp) in self.cache.items()
            if datetime.utcnow() > exp
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = len(self.cache)
        expired = sum(1 for _, (_, exp) in self.cache.items() if datetime.utcnow() > exp)

        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
            "ttl_minutes": self.ttl_minutes,
        }
