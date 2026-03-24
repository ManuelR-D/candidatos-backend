"""SenateSession service for database operations using SQLAlchemy ORM."""
from typing import Optional, List, cast
from datetime import date
from src.service.postgres_service import PostgreService
from src.dto.models.senate_session import SenateSession


class SenateSessionService:
    """Service for managing SenateSession database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize SenateSessionService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, session_date: date, session_type_id: Optional[int] = None) -> int:
        """
        Insert a senate session into the database.
        
        Args:
            session_date: Date of the session
            session_type_id: Optional ID of the session type
            
        Returns:
            The unique_id of the inserted session
        """
        with self.db.session_scope() as session:
            senate_session = SenateSession(
                Date=session_date,
                Session_type_id=session_type_id
            )
            session.add(senate_session)
            session.flush()  # Flush to get the generated ID
            return cast(int, senate_session.UniqueID)
    
    def insert_many(self, session_dates: List[date]) -> None:
        """
        Insert multiple senate sessions into the database.
        
        Args:
            session_dates: List of session dates
        """
        with self.db.session_scope() as session:
            senate_sessions = [SenateSession(Date=d) for d in session_dates]
            session.add_all(senate_sessions)
    
    def get_by_id(self, unique_id: int) -> SenateSession:
        """
        Get a senate session by its unique ID.
        
        Args:
            unique_id: SenateSession unique ID
            
        Returns:
            SenateSession ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            senate_session = session.query(SenateSession).filter(
                SenateSession.UniqueID == unique_id
            ).first()
            if senate_session is None:
                raise ValueError(f"SenateSession with UniqueID {unique_id} not found.")

            if senate_session:
                session.expunge(senate_session)  # Detach from session
            return senate_session
    
    def get_by_date(self, session_date: date) -> Optional[SenateSession]:
        """
        Get a senate session by its date.
        
        Args:
            session_date: Session date
            
        Returns:
            SenateSession ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            senate_session = session.query(SenateSession).filter(
                SenateSession.Date == session_date
            ).first()
            if senate_session:
                session.expunge(senate_session)  # Detach from session
            return senate_session

    def get_by_date_and_type(self, session_date: date, session_type_id: Optional[int]) -> Optional[SenateSession]:
        """
        Get a senate session by its date and session type.

        Args:
            session_date: Session date
            session_type_id: Optional session type ID

        Returns:
            SenateSession ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            senate_session = session.query(SenateSession).filter(
                SenateSession.Date == session_date,
                SenateSession.Session_type_id == session_type_id
            ).first()
            if senate_session:
                session.expunge(senate_session)  # Detach from session
            return senate_session

    def upsert(self, session_date: date, session_type_id: Optional[int] = None) -> int:
        """
        Insert a senate session if it doesn't exist; otherwise return existing ID.

        Args:
            session_date: Date of the session
            session_type_id: Optional ID of the session type

        Returns:
            The unique_id of the existing or inserted session
        """
        with self.db.session_scope() as session:
            existing = session.query(SenateSession).filter(
                SenateSession.Date == session_date,
                SenateSession.Session_type_id == session_type_id
            ).first()
            if existing:
                session.expunge(existing)
                return cast(int, existing.UniqueID)

            senate_session = SenateSession(
                Date=session_date,
                Session_type_id=session_type_id
            )
            session.add(senate_session)
            session.flush()  # Flush to get the generated ID
            return cast(int, senate_session.UniqueID)
    
    def get_all(self) -> List[SenateSession]:
        """
        Get all senate sessions from the database.
        
        Returns:
            List of SenateSession ORM objects
        """
        with self.db.session_scope() as session:
            senate_sessions = session.query(SenateSession).order_by(
                SenateSession.Date.desc()
            ).all()
            for ss in senate_sessions:
                session.expunge(ss)  # Detach from session
            return senate_sessions
