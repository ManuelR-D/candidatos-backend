"""Topic service for database operations using SQLAlchemy ORM."""
from typing import Optional, List, cast
from src.service.postgres_service import PostgreService
from src.dto.models.topic import Topic


class TopicService:
    """Service for managing Topic database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize TopicService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, senate_session_id: int, name: str) -> int:
        """
        Insert a topic into the database.
        
        Args:
            senate_session_id: Senate session ID
            name: Topic name
            
        Returns:
            The unique_id of the inserted topic
        """
        with self.db.session_scope() as session:
            topic = Topic(SenateSession_id=senate_session_id, Name=name)
            session.add(topic)
            session.flush()  # Flush to get the generated ID
            return topic.UniqueID
    
    def insert_many(self, topics_data: List[dict]) -> None:
        """
        Insert multiple topics into the database.
        
        Args:
            topics_data: List of dictionaries with topic data
        """
        with self.db.session_scope() as session:
            topics = [
                Topic(SenateSession_id=data['senate_session_id'], Name=data['name'])
                for data in topics_data
            ]
            session.add_all(topics)
    
    def get_by_id(self, unique_id: int) -> Optional[Topic]:
        """
        Get a topic by its unique ID.
        
        Args:
            unique_id: Topic unique ID
            
        Returns:
            Topic ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            topic = session.query(Topic).filter(Topic.UniqueID == unique_id).first()
            if topic:
                session.expunge(topic)  # Detach from session
            return topic
    
    def get_by_session(self, session_id: int) -> List[Topic]:
        """
        Get all topics for a specific senate session.
        
        Args:
            session_id: Senate session ID
            
        Returns:
            List of Topic ORM objects
        """
        with self.db.session_scope() as session:
            topics = session.query(Topic).filter(
                Topic.SenateSession_id == session_id
            ).order_by(Topic.UniqueID).all()
            for topic in topics:
                session.expunge(topic)  # Detach from session
            return topics

    def get_by_session_and_name(self, session_id: int, name: str) -> Optional[Topic]:
        """
        Get a topic by session and name.

        Args:
            session_id: Senate session ID
            name: Topic name

        Returns:
            Topic ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            topic = session.query(Topic).filter(
                Topic.SenateSession_id == session_id,
                Topic.Name == name
            ).first()
            if topic:
                session.expunge(topic)
            return topic

    def upsert(self, senate_session_id: int, name: str) -> int:
        """
        Insert a topic if it doesn't exist for the session; otherwise return existing ID.

        Args:
            senate_session_id: Senate session ID
            name: Topic name

        Returns:
            The unique_id of the existing or inserted topic
        """
        with self.db.session_scope() as session:
            existing = session.query(Topic).filter(
                Topic.SenateSession_id == senate_session_id,
                Topic.Name == name
            ).first()
            if existing:
                session.expunge(existing)
                return cast(int, existing.UniqueID)

            topic = Topic(SenateSession_id=senate_session_id, Name=name)
            session.add(topic)
            session.flush()  # Flush to get the generated ID
            return cast(int, topic.UniqueID)
    
    def get_all(self) -> List[Topic]:
        """
        Get all topics from the database.
        
        Returns:
            List of Topic ORM objects
        """
        with self.db.session_scope() as session:
            topics = session.query(Topic).order_by(
                Topic.SenateSession_id, Topic.UniqueID
            ).all()
            for topic in topics:
                session.expunge(topic)  # Detach from session
            return topics
