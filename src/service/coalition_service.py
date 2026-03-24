"""Coalition service for database operations using SQLAlchemy ORM."""
from typing import Optional, List
from src.service.postgres_service import PostgreService
from src.dto.models.coalition import Coalition


class CoalitionService:
    """Service for managing Coalition database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize CoalitionService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, name: str) -> int:
        """
        Insert a coalition into the database.
        
        Args:
            name: Coalition name
            
        Returns:
            The unique_id of the inserted coalition
        """
        with self.db.session_scope() as session:
            coalition = Coalition(Name=name)
            session.add(coalition)
            session.flush()
            return coalition.UniqueID
    
    def insert_many(self, names: List[str]) -> None:
        """
        Insert multiple coalitions into the database.
        
        Args:
            names: List of coalition names
        """
        with self.db.session_scope() as session:
            coalitions = [Coalition(Name=name) for name in names]
            session.add_all(coalitions)
    
    def get_by_id(self, unique_id: int) -> Optional[Coalition]:
        """
        Get a coalition by its unique ID.
        
        Args:
            unique_id: Coalition unique ID
            
        Returns:
            Coalition ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            coalition = session.query(Coalition).filter(Coalition.UniqueID == unique_id).first()
            if coalition:
                session.expunge(coalition)
            return coalition
    
    def get_by_name(self, name: str) -> Optional[Coalition]:
        """
        Get a coalition by its name.
        
        Args:
            name: Coalition name
            
        Returns:
            Coalition ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            coalition = session.query(Coalition).filter(Coalition.Name == name).first()
            if coalition:
                session.expunge(coalition)
            return coalition
    
    def get_all(self) -> List[Coalition]:
        """
        Get all coalitions from the database.
        
        Returns:
            List of Coalition ORM objects
        """
        with self.db.session_scope() as session:
            coalitions = session.query(Coalition).order_by(Coalition.Name).all()
            for coalition in coalitions:
                session.expunge(coalition)
            return coalitions
