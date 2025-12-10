"""Database configuration and setup."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import os

# Get database URL from environment or use SQLite default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///devops_command_center.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)

# Base class for models
Base = declarative_base()


@contextmanager
def get_db():
    """Get database session context manager."""
    db = Session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from backend.models import User, Task, Integration, IntegrationCredential, Notification
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


def reset_db():
    """Drop all tables and recreate (for development only)."""
    Base.metadata.drop_all(bind=engine)
    init_db()
    print("✅ Database reset successfully")

