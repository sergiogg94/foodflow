"""SQLite engine, session factory, and database initialization.

Concurrency per ADR-4: WAL mode, busy timeout, and foreign keys are enabled
on every connection so SQLite serializes writes and cannot corrupt data.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from .models import Base

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "data" / "foodflow.db"


def _db_path() -> Path:
    """Database file location.

    Defaults to <repo>/data/foodflow.db, which matches the docker-compose
    bind mount ./data:/app/data (ADR-3). Overridable via FOODFLOW_DB_PATH.
    """
    return Path(os.environ.get("FOODFLOW_DB_PATH", str(DEFAULT_DB_PATH)))


engine = create_engine(
    f"sqlite:///{_db_path()}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """Enable WAL mode, a busy timeout, and foreign key enforcement.

    WAL allows concurrent readers with a single writer; the busy timeout makes
    concurrent writers wait rather than fail; foreign keys make ON DELETE
    CASCADE work (required by FR-5).
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create the database file and all tables if they do not exist."""
    _db_path().parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency yielding a session for the lifetime of a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()