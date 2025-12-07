"""
Base model and database setup for ReqCockpit

This module provides the foundation for all database operations:
- DeclarativeBase for SQLAlchemy models
- DatabaseManager for connection lifecycle
- SQLite optimizations for performance
"""
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class DatabaseManager:
    """
    Manages database connections and sessions for ReqCockpit
    
    Implements single connection pattern to avoid SQLite locking issues.
    Provides transaction management and automatic backup functionality.
    """
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.current_db_path: Optional[str] = None
        
    def create_database(self, db_path: str) -> bool:
        """
        Create a new SQLite database with ReqCockpit schema
        
        Args:
            db_path: Full path to the database file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create engine with optimizations
            engine = create_engine(
                f"sqlite:///{db_path}",
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                },
                poolclass=StaticPool,
                echo=False
            )
            
            # Enable foreign keys
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
            
            # Create all tables
            Base.metadata.create_all(engine)
            
            logger.info(f"Database created successfully: {db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            return False
    
    def connect(self, db_path: str) -> bool:
        """
        Connect to an existing database
        
        Args:
            db_path: Full path to the database file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Close existing connection if any
            self.disconnect()
            
            # Create engine
            self.engine = create_engine(
                f"sqlite:///{db_path}",
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                },
                poolclass=StaticPool,
                echo=False
            )
            
            # Enable foreign keys and optimizations
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=-64000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.current_db_path = db_path
            
            logger.info(f"Connected to database: {db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close current database connection"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.session_factory = None
            self.current_db_path = None
            logger.info("Database connection closed")
    
    def get_session(self) -> Optional[Session]:
        """
        Get a new database session
        
        Returns:
            SQLAlchemy Session object or None if not connected
        """
        if not self.session_factory:
            logger.error("No database connection available")
            return None
        return self.session_factory()
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the current database
        
        Args:
            backup_path: Path for backup file (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.current_db_path:
            logger.error("No database connected for backup")
            return False
            
        try:
            import shutil
            
            if not backup_path:
                backup_path = f"{self.current_db_path}.backup"
            
            shutil.copy2(self.current_db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False
    
    def vacuum(self) -> bool:
        """
        Optimize database by running VACUUM
        
        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            return False
            
        try:
            with self.engine.connect() as conn:
                conn.execute("VACUUM")
            logger.info("Database vacuumed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()