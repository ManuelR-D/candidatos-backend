"""Party service for database operations using SQLAlchemy ORM."""
from typing import Optional, List
from src.service.postgres_service import PostgreService
from src.dto.models.party import Party


class PartyService:
    """Service for managing Party database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize PartyService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, name: str) -> int:
        """
        Insert a party into the database.
        
        Args:
            name: Party name
            
        Returns:
            The unique_id of the inserted party
        """
        with self.db.session_scope() as session:
            party = Party(Name=name)
            session.add(party)
            session.flush()
            return party.UniqueID
    
    def insert_many(self, names: List[str]) -> None:
        """
        Insert multiple parties into the database.
        
        Args:
            names: List of party names
        """
        with self.db.session_scope() as session:
            parties = [Party(Name=name) for name in names]
            session.add_all(parties)
    
    def get_by_id(self, unique_id: int) -> Optional[Party]:
        """
        Get a party by its unique ID.
        
        Args:
            unique_id: Party unique ID
            
        Returns:
            Party ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            party = session.query(Party).filter(Party.UniqueID == unique_id).first()
            if party:
                session.expunge(party)
            return party
    
    def get_by_name(self, name: str) -> Optional[Party]:
        """
        Get a party by its name.
        
        Args:
            name: Party name
            
        Returns:
            Party ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            party = session.query(Party).filter(Party.Name == name).first()
            if party:
                session.expunge(party)
            return party
    
    def get_all(self) -> List[Party]:
        """
        Get all parties from the database.
        
        Returns:
            List of Party ORM objects
        """
        with self.db.session_scope() as session:
            parties = session.query(Party).order_by(Party.Name).all()
            for party in parties:
                session.expunge(party)
            return parties
