"""VoteSession service for database operations using SQLAlchemy ORM."""
from typing import Optional, List
from uuid import UUID
from src.service.postgres_service import PostgreService
from src.dto.models.vote_session import VoteSession


class VoteSessionService:
    """Service for managing VoteSession database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize VoteSessionService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, representative_id: UUID, senate_session_id: int, topic_id: int, vote_id: int) -> int:
        """
        Insert a vote session into the database.
        
        Args:
            representative_id: Representative UUID
            senate_session_id: Senate session ID
            topic_id: Topic ID
            vote_id: Vote ID
            
        Returns:
            The unique_id of the inserted vote session
        """
        with self.db.session_scope() as session:
            vote_session = VoteSession(
                Representative_id=representative_id,
                SenateSession_id=senate_session_id,
                Topic_id=topic_id,
                Vote_id=vote_id
            )
            session.add(vote_session)
            session.flush()
            return vote_session.UniqueID
    
    def insert_many(self, vote_sessions_data: List[dict]) -> None:
        """
        Insert multiple vote sessions into the database.
        
        Args:
            vote_sessions_data: List of dictionaries with vote session data
        """
        with self.db.session_scope() as session:
            vote_sessions = [
                VoteSession(
                    Representative_id=data['representative_id'],
                    SenateSession_id=data['senate_session_id'],
                    Topic_id=data['topic_id'],
                    Vote_id=data['vote_id']
                )
                for data in vote_sessions_data
            ]
            session.add_all(vote_sessions)
    
    def get_by_id(self, unique_id: int) -> Optional[VoteSession]:
        """
        Get a vote session by its unique ID.
        
        Args:
            unique_id: VoteSession unique ID
            
        Returns:
            VoteSession ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            vote_session = session.query(VoteSession).filter(
                VoteSession.UniqueID == unique_id
            ).first()
            if vote_session:
                session.expunge(vote_session)
            return vote_session
    
    def get_by_session(self, session_id: int) -> List[VoteSession]:
        """
        Get all vote records for a specific senate session.
        
        Args:
            session_id: Senate session ID
            
        Returns:
            List of VoteSession ORM objects
        """
        with self.db.session_scope() as session:
            vote_sessions = session.query(VoteSession).filter(
                VoteSession.SenateSession_id == session_id
            ).all()
            for vs in vote_sessions:
                session.expunge(vs)
            return vote_sessions
    
    def get_by_topic(self, topic_id: int) -> List[VoteSession]:
        """
        Get all vote records for a specific topic.
        
        Args:
            topic_id: Topic ID
            
        Returns:
            List of VoteSession ORM objects
        """
        with self.db.session_scope() as session:
            vote_sessions = session.query(VoteSession).filter(
                VoteSession.Topic_id == topic_id
            ).all()
            for vs in vote_sessions:
                session.expunge(vs)
            return vote_sessions
    
    def get_by_representative(self, representative_id: UUID) -> List[VoteSession]:
        """
        Get all vote records for a specific representative.
        
        Args:
            representative_id: Representative UUID
            
        Returns:
            List of VoteSession ORM objects
        """
        with self.db.session_scope() as session:
            vote_sessions = session.query(VoteSession).filter(
                VoteSession.Representative_id == representative_id
            ).all()
            for vs in vote_sessions:
                session.expunge(vs)
            return vote_sessions
