"""Shared fixtures for the FoodFlow backend test suite (NB-3).

The app reads FOODFLOW_DB_PATH at import time (backend/app/db.py), so the
client fixture re-imports the app modules per test against a fresh temp SQLite
file, giving each test an isolated database.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """TestClient bound to an isolated SQLite database for each test."""
    monkeypatch.setenv("FOODFLOW_DB_PATH", str(tmp_path / "test.db"))
    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            del sys.modules[module_name]
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client