"""Vote service for database operations using SQLAlchemy ORM."""
from typing import Optional, List
from src.service.postgres_service import PostgreService
from src.dto.models.vote import Vote


class VoteService:
    """Service for managing Vote database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize VoteService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, name: str) -> int:
        """
        Insert a vote type into the database.
        
        Args:
            name: Vote name
            
        Returns:
            The unique_id of the inserted vote
        """
        with self.db.session_scope() as session:
            vote = Vote(Name=name)
            session.add(vote)
            session.flush()
            return vote.UniqueID
    
    def insert_many(self, names: List[str]) -> None:
        """
        Insert multiple vote types into the database.
        
        Args:
            names: List of vote names
        """
        with self.db.session_scope() as session:
            votes = [Vote(Name=name) for name in names]
            session.add_all(votes)
    
    def get_by_id(self, unique_id: int) -> Optional[Vote]:
        """
        Get a vote type by its unique ID.
        
        Args:
            unique_id: Vote unique ID
            
        Returns:
            Vote ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            vote = session.query(Vote).filter(Vote.UniqueID == unique_id).first()
            if vote:
                session.expunge(vote)
            return vote
    
    def get_by_name(self, name: str) -> Optional[Vote]:
        """
        Get a vote type by its name.
        
        Args:
            name: Vote name
            
        Returns:
            Vote ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            vote = session.query(Vote).filter(Vote.Name == name).first()
            if vote:
                session.expunge(vote)
            return vote
    
    def get_all(self) -> List[Vote]:
        """
        Get all vote types from the database.
        
        Returns:
            List of Vote ORM objects
        """
        with self.db.session_scope() as session:
            votes = session.query(Vote).all()
            for vote in votes:
                session.expunge(vote)
            return votes
