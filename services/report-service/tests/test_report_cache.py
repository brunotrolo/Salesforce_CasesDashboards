import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.report_cache import ReportCache
from src.models.report import ReportExecutionResult


@pytest.fixture
def cache():
    """Create a cache instance."""
    return ReportCache(ttl_minutes=60)


@pytest.fixture
def sample_result():
    """Create a sample execution result."""
    return ReportExecutionResult(
        report_id="report:123",
        status="success",
        rows_returned=42,
        execution_time_ms=250,
        executed_at=datetime.utcnow(),
        data=[{"id": "1", "name": "Test"}],
    )


class TestReportCache:
    def test_cache_key_generation(self, cache):
        """Test cache key generation."""
        key1 = cache.get_cache_key("report:123")
        key2 = cache.get_cache_key("report:123")

        assert key1 == key2
        assert "report:123" in key1

    def test_cache_key_with_filters(self, cache):
        """Test cache key includes filters."""
        filters1 = {"status": "open"}
        filters2 = {"status": "open"}
        filters3 = {"status": "closed"}

        key1 = cache.get_cache_key("report:123", filters1)
        key2 = cache.get_cache_key("report:123", filters2)
        key3 = cache.get_cache_key("report:123", filters3)

        assert key1 == key2
        assert key1 != key3

    def test_set_and_get(self, cache):
        """Test setting and getting cache entries."""
        cache.set("key:1", "value:1")
        result = cache.get("key:1")

        assert result == "value:1"

    def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key returns None."""
        result = cache.get("non:existent")
        assert result is None

    def test_cache_expiration(self, cache):
        """Test cache entries can be set with custom TTL."""
        cache.set("key:1", "value:1", ttl_minutes=60)
        result = cache.get("key:1")
        # Entry was just set, should be available
        assert result == "value:1"

    def test_cache_result(self, cache, sample_result):
        """Test caching a report result."""
        cache.cache_result("report:123", sample_result)
        retrieved = cache.get_cached_result("report:123")

        assert retrieved is not None
        assert retrieved.report_id == "report:123"
        assert retrieved.rows_returned == 42

    def test_cache_result_with_filters(self, cache, sample_result):
        """Test caching result with filters."""
        filters = {"status": "open"}

        cache.cache_result("report:123", sample_result, filters)
        retrieved = cache.get_cached_result("report:123", filters)

        assert retrieved is not None
        assert retrieved.status == "success"

    def test_cache_result_filters_matter(self, cache, sample_result):
        """Test different filters get different cache entries."""
        filters1 = {"status": "open"}
        filters2 = {"status": "closed"}

        cache.cache_result("report:123", sample_result, filters1)

        # Should not get result cached with different filters
        retrieved = cache.get_cached_result("report:123", filters2)
        assert retrieved is None

    def test_invalidate_report(self, cache, sample_result):
        """Test invalidating all report entries."""
        cache.cache_result("report:123", sample_result)
        cache.cache_result("report:123", sample_result, {"status": "open"})
        cache.cache_result("report:456", sample_result)

        invalidated = cache.invalidate_report("report:123")

        assert invalidated >= 1  # At least one entry invalidated
        assert cache.get_cached_result("report:123") is None
        assert cache.get_cached_result("report:456") is not None

    def test_clear_cache(self, cache, sample_result):
        """Test clearing entire cache."""
        cache.cache_result("report:123", sample_result)
        cache.cache_result("report:456", sample_result)

        cache.clear()

        assert cache.get_cached_result("report:123") is None
        assert cache.get_cached_result("report:456") is None

    def test_cleanup_expired(self, cache, sample_result):
        """Test cleaning up expired entries."""
        from datetime import timedelta

        cache.set("key:1", "value:1", ttl_minutes=60)
        cache.set("key:2", "value:2", ttl_minutes=1)

        # Manually set key:2 to expire in the past
        cache.cache["key:2"] = ("value:2", datetime.utcnow() - timedelta(seconds=1))

        cleaned = cache.cleanup_expired()

        assert cleaned >= 1
        assert cache.get("key:1") is not None
        assert cache.get("key:2") is None

    def test_stats(self, cache, sample_result):
        """Test getting cache statistics."""
        cache.cache_result("report:123", sample_result)
        cache.cache_result("report:456", sample_result)

        stats = cache.stats()

        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2
        assert stats["ttl_minutes"] == 60

    def test_custom_ttl(self, cache):
        """Test setting custom TTL."""
        cache.set("key:1", "value:1", ttl_minutes=120)

        result = cache.get("key:1")
        assert result == "value:1"

    def test_cache_complex_data(self, cache):
        """Test caching complex data structures."""
        complex_data = {
            "records": [
                {"id": 1, "name": "Record 1"},
                {"id": 2, "name": "Record 2"},
            ],
            "metadata": {"total": 2, "page": 1}
        }

        cache.set("complex:key", complex_data)
        retrieved = cache.get("complex:key")

        assert retrieved == complex_data
        assert len(retrieved["records"]) == 2

    def test_cache_overwrite(self, cache):
        """Test overwriting cache entries."""
        cache.set("key:1", "value:1")
        assert cache.get("key:1") == "value:1"

        cache.set("key:1", "value:2")
        assert cache.get("key:1") == "value:2"
