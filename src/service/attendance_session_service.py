"""AttendanceSession service for database operations using SQLAlchemy ORM."""
from typing import Optional, List
from uuid import UUID
from src.service.postgres_service import PostgreService
from src.dto.models.attendance_session import AttendanceSession


class AttendanceSessionService:
    """Service for managing AttendanceSession database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize AttendanceSessionService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, representative_id: UUID, senate_session_id: int, attendance_id: int) -> int:
        """
        Insert an attendance session into the database.
        
        Args:
            representative_id: Representative UUID
            senate_session_id: Senate session ID
            attendance_id: Attendance ID
            
        Returns:
            The unique_id of the inserted attendance session
        """
        with self.db.session_scope() as session:
            attendance_session = AttendanceSession(
                Representative_id=representative_id,
                SenateSession_id=senate_session_id,
                Attendance_id=attendance_id
            )
            session.add(attendance_session)
            session.flush()
            return attendance_session.UniqueID
    
    def insert_many(self, attendance_sessions_data: List[dict]) -> None:
        """
        Insert multiple attendance sessions into the database.
        
        Args:
            attendance_sessions_data: List of dictionaries with attendance session data
        """
        with self.db.session_scope() as session:
            attendance_sessions = [
                AttendanceSession(
                    Representative_id=data['representative_id'],
                    SenateSession_id=data['senate_session_id'],
                    Attendance_id=data['attendance_id']
                )
                for data in attendance_sessions_data
            ]
            session.add_all(attendance_sessions)
    
    def get_by_id(self, unique_id: int) -> Optional[AttendanceSession]:
        """
        Get an attendance session by its unique ID.
        
        Args:
            unique_id: AttendanceSession unique ID
            
        Returns:
            AttendanceSession ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            attendance_session = session.query(AttendanceSession).filter(
                AttendanceSession.UniqueID == unique_id
            ).first()
            if attendance_session:
                session.expunge(attendance_session)
            return attendance_session
    
    def get_by_session(self, session_id: int) -> List[AttendanceSession]:
        """
        Get all attendance records for a specific senate session.
        
        Args:
            session_id: Senate session ID
            
        Returns:
            List of AttendanceSession ORM objects
        """
        with self.db.session_scope() as session:
            attendance_sessions = session.query(AttendanceSession).filter(
                AttendanceSession.SenateSession_id == session_id
            ).all()
            for att in attendance_sessions:
                session.expunge(att)
            return attendance_sessions
    
    def get_by_representative(self, representative_id: UUID) -> List[AttendanceSession]:
        """
        Get all attendance records for a specific representative.
        
        Args:
            representative_id: Representative UUID
            
        Returns:
            List of AttendanceSession ORM objects
        """
        with self.db.session_scope() as session:
            attendance_sessions = session.query(AttendanceSession).filter(
                AttendanceSession.Representative_id == representative_id
            ).all()
            for att in attendance_sessions:
                session.expunge(att)
            return attendance_sessions
