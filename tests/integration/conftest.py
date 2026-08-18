"""Conftest para testes de integração.

Carrega módulos de cada serviço sob o pacote `src` de forma isolada:
todos os serviços usam o nome `src`, o que colide num mesmo processo.
O ServiceLoader troca o sys.path e limpa sys.modules["src.*"] entre cargas.
"""

import importlib
import sys
from pathlib import Path

SERVICES_ROOT = Path(__file__).resolve().parents[2] / "services"


class ServiceLoader:
    """Context manager que carrega módulos de um serviço específico."""

    def __init__(self, service_dir: str):
        self.src = SERVICES_ROOT / service_dir / "src"
        self._saved = {}

    def __enter__(self):
        sys.path.insert(0, str(self.src))
        self._saved = {
            k: sys.modules.pop(k)
            for k in list(sys.modules)
            if k == "src" or k.startswith("src.")
        }
        return self

    def __exit__(self, *args):
        for k in list(sys.modules):
            if k == "src" or k.startswith("src."):
                del sys.modules[k]
        sys.modules.update(self._saved)
        sys.path.remove(str(self.src))

    def import_module(self, name: str):
        return importlib.import_module(f"src.{name}")


def load_auth():
    """Carrega módulos do auth-service (JWT, RBAC)."""
    with ServiceLoader("auth-service") as loader:
        return {
            "JWTHandler": loader.import_module("jwt_handler").JWTHandler,
            "RBAC": loader.import_module("rbac").RBAC,
        }


def load_mcp():
    """Carrega módulos do mcp-client (OAuth)."""
    with ServiceLoader("mcp-client") as loader:
        return {
            "OAuthHandler": loader.import_module("oauth_handler").OAuthHandler,
        }