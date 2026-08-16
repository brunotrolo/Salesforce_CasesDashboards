"""Test configuration for API Gateway."""

import pytest
from fastapi.testclient import TestClient
import sys
import os
from pathlib import Path

# Ensure services directory is in path for relative imports
# This is needed because the API Gateway imports from other services
services_dir = Path(__file__).parent.parent.parent
if str(services_dir) not in sys.path:
    sys.path.insert(0, str(services_dir))

# Also add the api-gateway src directory for direct imports
api_gateway_src = Path(__file__).parent.parent / "src"
if str(api_gateway_src) not in sys.path:
    sys.path.insert(0, str(api_gateway_src))


@pytest.fixture
def client():
    """Create a test client for the API."""
    print(f"\n[CONFTEST] Current dir: {os.getcwd()}", flush=True)
    print(f"[CONFTEST] sys.path[0]: {sys.path[0]}", flush=True)

    # Set environment variables to prevent auth errors during testing
    os.environ.setdefault("SF_CLIENT_ID", "test")
    os.environ.setdefault("SF_CLIENT_SECRET", "test")
    os.environ.setdefault("SF_REFRESH_TOKEN", "test")

    # Import main after environment is set
    try:
        print("[CONFTEST] Attempting to import main...", flush=True)
        from main import app
        print("[CONFTEST] Successfully imported app", flush=True)
    except Exception as e:
        print(f"[CONFTEST] Failed to import app: {type(e).__name__}: {e}", flush=True)
        raise

    try:
        print("[CONFTEST] Creating TestClient...", flush=True)
        client = TestClient(app)
        print("[CONFTEST] Successfully created TestClient", flush=True)
        return client
    except Exception as e:
        print(f"[CONFTEST] Failed to create TestClient: {type(e).__name__}: {e}", flush=True)
        raise
