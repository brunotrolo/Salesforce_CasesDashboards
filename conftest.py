"""Root conftest for pytest configuration."""

import sys
from pathlib import Path

# Add services directory and each service's src to Python path
# This allows tests to import from their services using relative imports
repo_root = Path(__file__).parent
services_dir = repo_root / "services"

# Add main services directory
sys.path.insert(0, str(services_dir))

# Add each service's src directory so tests can use 'from src.module import X'
for service_path in services_dir.iterdir():
    if service_path.is_dir() and not service_path.name.startswith('.'):
        src_path = service_path / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
