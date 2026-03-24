"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

# Create the declarative base
Base = declarative_base()

# Database configuration
DEFAULT_DATABASE_URL = "postgresql://senate_user:senate_pass@localhost:5433/senate_db"


class DatabaseManager:
    """Manages database connections and sessions using SQLAlchemy."""
    
    def __init__(self, database_url: str = DEFAULT_DATABASE_URL):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using them
            echo=False  # Set to True for SQL query logging during development
        )
        
        # Create a session factory
        self.session_factory = sessionmaker(bind=self.engine)
        
        # Create a scoped session for thread-safe operations
        self.Session = scoped_session(self.session_factory)
    
    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope for a series of operations.
        
        Usage:
            with db_manager.session_scope() as session:
                session.add(obj)
                # ... more operations
        
        The session will automatically commit if no exceptions occur,
        or rollback if an exception is raised.
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)
    
    def drop_all_tables(self):
        """Drop all tables in the database (use with caution!)."""
        Base.metadata.drop_all(self.engine)
    
    def dispose(self):
        """Dispose of the connection pool."""
        self.engine.dispose()
