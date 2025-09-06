"""
Database configuration and setup for Phase 5B
Supports both SQLite (local) and PostgreSQL (production)
"""
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

try:
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    from typing import Generator
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    # Handle missing SQLAlchemy gracefully
    SQLALCHEMY_AVAILABLE = False
    logger.warning("⚠️  SQLAlchemy not installed. Database features disabled.")
    
    # Create dummy classes
    class Session:
        pass
    
    def sessionmaker(*args, **kwargs):
        return lambda: Session()
    
    def declarative_base():
        return type('Base', (), {})
    
    def create_engine(*args, **kwargs):
        return None

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voice_ai.db")

# Create engine only if SQLAlchemy is available
if SQLALCHEMY_AVAILABLE:
    if DATABASE_URL.startswith("sqlite"):
        # SQLite configuration
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL configuration
        engine = create_engine(DATABASE_URL)

    # Create SessionLocal class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create Base class for models
    Base = declarative_base()

    def get_db() -> Generator[Session, None, None]:
        """Dependency to get database session"""
        if not SQLALCHEMY_AVAILABLE:
            yield None
            return
            
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_tables():
        """Create all database tables"""
        if SQLALCHEMY_AVAILABLE and engine:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        else:
            logger.warning("Database not available, skipping table creation")

else:
    engine = None
    SessionLocal = None
    Base = None
    
    def get_db():
        yield None
    
    def create_tables():
        logger.warning("Database not available, skipping table creation")
