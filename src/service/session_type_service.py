"""SessionType service for database operations using SQLAlchemy ORM."""
from typing import Optional, List
from src.service.postgres_service import PostgreService
from src.dto.models.session_type import SessionType


class SessionTypeService:
    """Service for managing SessionType database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize SessionTypeService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def get_by_id(self, unique_id: int) -> Optional[SessionType]:
        """
        Get a session type by its unique ID.
        
        Args:
            unique_id: SessionType unique ID
            
        Returns:
            SessionType ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            return session.query(SessionType).filter(
                SessionType.UniqueID == unique_id
            ).first()
    
    def get_by_short_name(self, short_name: str) -> Optional[SessionType]:
        """
        Get a session type by its short name.
        
        Args:
            short_name: SessionType short name (e.g., 'OR', 'EX', 'AS')
            
        Returns:
            SessionType ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            result = session.query(SessionType).filter(
                SessionType.Short_name == short_name.upper()
            ).first()
            
            if result:
                # Force load the UniqueID attribute before session closes
                session.refresh(result)
                return result
            return None
    
    def get_id_by_short_name(self, short_name: str) -> Optional[int]:
        """
        Get a session type ID by its short name.
        
        Args:
            short_name: SessionType short name (e.g., 'OR', 'EX', 'AS')
            
        Returns:
            SessionType ID if found, None otherwise
        """
        with self.db.session_scope() as session:
            result = session.query(SessionType.UniqueID).filter(
                SessionType.Short_name == short_name.upper()
            ).scalar()
            return result
    
    def get_by_name(self, name: str) -> Optional[SessionType]:
        """
        Get a session type by its full name.
        
        Args:
            name: SessionType full name
            
        Returns:
            SessionType ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            return session.query(SessionType).filter(
                SessionType.Name == name.upper()
            ).first()
    
    def get_all(self) -> List[SessionType]:
        """
        Get all session types.
        
        Returns:
            List of SessionType ORM objects
        """
        with self.db.session_scope() as session:
            return session.query(SessionType).order_by(SessionType.Name).all()
