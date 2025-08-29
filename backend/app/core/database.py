"""
Capitol Engineering Company - Database Configuration
SQLAlchemy database setup for PostgreSQL
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL from environment - use PostgreSQL in production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./capitol_takeoff.db")

# Configure SQLAlchemy engine with proper settings for production
if DATABASE_URL.startswith("postgresql"):
    # Production PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "connect_timeout": 60,
            "application_name": "capitol-takeoff"
        }
    )
else:
    # Development SQLite configuration
    engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()