"""
===============================================================================
NWIS Backend - Database Engine & Session Management
===============================================================================
Connects FastAPI to PostgreSQL using SQLAlchemy with connection pooling and
safe session cleanup.
===============================================================================
"""

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Read database credentials or full connection URL from environment
DATABASE_URL_ENV = os.getenv("DATABASE_URL")

if DATABASE_URL_ENV:
    if DATABASE_URL_ENV.startswith("postgresql://"):
        SQLALCHEMY_DATABASE_URL = DATABASE_URL_ENV.replace("postgresql://", "postgresql+psycopg2://", 1)
    else:
        SQLALCHEMY_DATABASE_URL = DATABASE_URL_ENV
else:
    DB_HOST = os.getenv("DATABASE_HOST", "localhost")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")
    DB_NAME = os.getenv("DATABASE_NAME", "nwis_db")
    DB_USER = os.getenv("DATABASE_USER", "nwis_user")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "nwis_password")

    # Safely URL-encode credentials to handle special characters
    ENCODED_USER = quote_plus(DB_USER)
    ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

    # Construct PostgreSQL connection URL (psycopg2 driver)
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{ENCODED_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# Create SQLAlchemy engine with connection health check (pool_pre_ping=True)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory for handling requests
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a transactional database session per request
    and guarantees proper session closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Utility to check if PostgreSQL is reachable.
    Used by /api/health/db endpoint.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
