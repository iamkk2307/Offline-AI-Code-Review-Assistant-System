"""
Database Connection & Initialization
=====================================
Manages the SQLAlchemy engine, session factory, and schema creation.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from database.models import Base

# Module-level engine and session factory (initialized once)
_engine = None
_SessionLocal = None


def init_db(database_url: str) -> None:
    """
    Initialize the database engine and create all tables.
    Safe to call multiple times (idempotent).
    
    Args:
        database_url: SQLAlchemy database URL string.
    """
    global _engine, _SessionLocal
    
    # SQLite specific: ensure the directory exists
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    _engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # Allow multi-threaded SQLite
        echo=False,
        pool_pre_ping=True,
    )
    
    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=_engine)
    logger.info(f"Database initialized: {database_url}")


def get_session() -> Session:
    """Return a new database session. Caller is responsible for closing."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager that provides a database session with automatic
    commit/rollback and cleanup.
    
    Usage:
        with get_db_session() as session:
            repo = ProjectRepository(session)
            project = repo.get_by_id(1)
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()
