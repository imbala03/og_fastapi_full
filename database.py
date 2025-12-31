"""
Database configuration module for the OG Soda FastAPI service.

This module handles:
- SQLAlchemy engine creation
- SessionLocal for database sessions
- Base class for ORM models
- get_db() dependency for FastAPI routes

Environment Support:
- dev_local: Local development database
- staging: Render PostgreSQL database (production)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Detect if running on Render
IS_RENDER = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_NAME") or os.getenv("RENDER_EXTERNAL_URL"))

# Get environment (dev_local, staging, or production)
# If on Render and ENV not set, default to staging
if IS_RENDER and not os.getenv("ENV"):
    ENV = "staging"
else:
    ENV = os.getenv("ENV", "dev_local")


# -----------------------------
# DATABASE CONNECTION URL
# -----------------------------

# Database URLs for different environments
DATABASE_URLS = {
    "dev_local": "postgresql://postgres:Bala03@localhost:5432/og_database",
    "staging": "postgresql://og_user:4cju7zo9oKzqdnDijYWQpIE4fyBQBeGm@dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com/og_database_0vc9",
    "production": os.getenv("DATABASE_URL", "")  # For Render production
}

# Get database URL based on environment
# Priority: DATABASE_URL env var > environment-specific config
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # If DATABASE_URL is not set, use environment-specific config
    if ENV in DATABASE_URLS:
        DATABASE_URL = DATABASE_URLS[ENV]
    else:
        # Fallback to dev_local
        DATABASE_URL = DATABASE_URLS["dev_local"]
    
    # Log warning if using fallback on Render
    if os.getenv("RENDER") or os.getenv("ENV") == "staging":
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"DATABASE_URL not set! Using fallback for ENV={ENV}")
        logger.warning(f"Please link your database in Render dashboard or set DATABASE_URL environment variable")


# -----------------------------
# SQLALCHEMY ENGINE + SESSION
# -----------------------------

# Create engine with connection pooling for better performance
# Render free tier has limited database connections (max 5-10)
# Using conservative pool sizes to avoid connection limit errors
if ENV == "staging" or os.getenv("RENDER"):
    # Render free tier: Use smaller pool to stay within limits
    pool_size = 3
    max_overflow = 2  # Total max: 5 connections
else:
    # Local development: Can use more connections
    pool_size = 10
    max_overflow = 20

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=pool_size,
    max_overflow=max_overflow,
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
