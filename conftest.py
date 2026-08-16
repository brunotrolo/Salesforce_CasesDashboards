"""Root conftest for pytest configuration."""

import sys
from pathlib import Path

# Add services directory to Python path so relative imports work
services_path = Path(__file__).parent / "services"
sys.path.insert(0, str(services_path))
