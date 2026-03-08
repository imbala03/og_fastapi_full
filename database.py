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

# Detect if running on Render (check multiple indicators)
IS_RENDER = bool(
    os.getenv("RENDER") or 
    os.getenv("RENDER_SERVICE_NAME") or 
    os.getenv("RENDER_EXTERNAL_URL") or
    os.getenv("RENDER_SERVICE_ID") or
    "/opt/render" in os.getcwd()  # Render uses /opt/render/project
)

# Get environment (dev_local, staging, or production)
# If on Render and ENV not set, default to staging
if IS_RENDER and not os.getenv("ENV"):
    ENV = "staging"
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("🔵 Render environment detected - using staging configuration")
else:
    ENV = os.getenv("ENV", "dev_local")


# -----------------------------
# DATABASE CONNECTION URL
# -----------------------------

# Database URLs for different environments
DATABASE_URLS = {
    "dev_local": "postgresql://postgres:Bala03@localhost:5432/og_database",
    "staging": "postgresql://og_database_30df_user:s39cVEANajU2fxGhYnz0KaFmEIGP4Lnt@dpg-d6l1cahaae7s73ft7os0-a.oregon-postgres.render.com/og_database_30df",
    "production": os.getenv("DATABASE_URL", "")  # For Render production (set by Render when DB is linked)
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

# Render PostgreSQL (internal or external) may require SSL
if DATABASE_URL and "sslmode=" not in DATABASE_URL:
    is_render_db = (
        "render.com" in DATABASE_URL
        or "oregon-postgres.render.com" in DATABASE_URL
        or "@dpg-" in DATABASE_URL  # internal host e.g. dpg-d6l1cahaae7s73ft7os0-a
    )
    if is_render_db:
        _sep = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL = f"{DATABASE_URL}{_sep}sslmode=require"


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
# STARTUP MIGRATIONS (add columns if missing; no DB shell needed on free hosting)
# -----------------------------

def run_additive_migrations(eng):
    """
    Add new columns to existing tables if they don't exist.
    Safe to run on every startup; uses IF NOT EXISTS so idempotent.
    Allows free-tier hosting (e.g. Render) to work without manual DB shell.
    """
    from sqlalchemy import text
    migrations = [
        "ALTER TABLE order_temp ADD COLUMN IF NOT EXISTS bottles_taken INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS bottles_taken INTEGER NOT NULL DEFAULT 0",
    ]
    for sql in migrations:
        try:
            with eng.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
        except Exception as e:
            # Log but don't fail startup (e.g. table might not exist yet)
            import logging
            logging.getLogger(__name__).warning(f"Additive migration skipped: {e}")


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
