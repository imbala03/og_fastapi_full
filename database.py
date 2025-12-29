"""
Database configuration module for the OG Soda FastAPI service.

This module handles:
- SQLAlchemy engine creation
- SessionLocal for database sessions
- Base class for ORM models
- get_db() dependency for FastAPI routes
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# -----------------------------
# DATABASE CONNECTION URL
# -----------------------------

# Get database URL from environment variable, with fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Bala03@localhost:5432/og_database"
)


# -----------------------------
# SQLALCHEMY ENGINE + SESSION
# -----------------------------

# Create engine with connection pooling for better performance
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Maximum number of connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before using them
    echo=False  # Set to True for SQL query logging (debugging)
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Base class for all models
Base = declarative_base()


# -----------------------------
# DEPENDENCY: GET DB SESSION
# -----------------------------

def get_db():
    """
    Creates a new SQLAlchemy database session for each request.

    This function is used in FastAPI dependency injection.
    It ensures:
    - opening a DB session before request
    - closing the session after request is finished
    - proper transaction rollback on errors
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit if no exceptions
    except Exception:
        db.rollback()  # Rollback on any error
        raise
    finally:
        db.close()
