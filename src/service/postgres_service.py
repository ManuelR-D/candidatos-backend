"""PostgreSQL database connection service using SQLAlchemy ORM."""
from src.database import DatabaseManager


class PostgreService:
    """Service for managing PostgreSQL database connections using SQLAlchemy."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5433,
        database: str = "senate_db",
        user: str = "senate_user",
        password: str = "senate_pass"
    ):
        """
        Initialize PostgreSQL connection using SQLAlchemy.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.db_manager = DatabaseManager(database_url)
    
    def session_scope(self):
        """
        Get a database session context manager.
        
        Returns:
            Context manager for database session
            
        Usage:
            with postgres_service.session_scope() as session:
                # Use session for database operations
                session.add(obj)
        """
        return self.db_manager.session_scope()
    
    def create_all_tables(self):
        """Create all tables in the database."""
        self.db_manager.create_all_tables()
    
    def dispose(self):
        """Dispose of the connection pool."""
        self.db_manager.dispose()

