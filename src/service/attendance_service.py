"""Attendance service for database operations using SQLAlchemy ORM."""
from typing import Optional, List
from src.service.postgres_service import PostgreService
from src.dto.models.attendance import Attendance


class AttendanceService:
    """Service for managing Attendance database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize AttendanceService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, name: str) -> int:
        """
        Insert an attendance type into the database.
        
        Args:
            name: Attendance name
            
        Returns:
            The unique_id of the inserted attendance
        """
        with self.db.session_scope() as session:
            attendance = Attendance(Name=name)
            session.add(attendance)
            session.flush()
            return attendance.UniqueID
    
    def insert_many(self, names: List[str]) -> None:
        """
        Insert multiple attendance types into the database.
        
        Args:
            names: List of attendance names
        """
        with self.db.session_scope() as session:
            attendances = [Attendance(Name=name) for name in names]
            session.add_all(attendances)
    
    def get_by_id(self, unique_id: int) -> Optional[Attendance]:
        """
        Get an attendance type by its unique ID.
        
        Args:
            unique_id: Attendance unique ID
            
        Returns:
            Attendance ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            attendance = session.query(Attendance).filter(Attendance.UniqueID == unique_id).first()
            if attendance:
                session.expunge(attendance)
            return attendance
    
    def get_by_name(self, name: str) -> Optional[Attendance]:
        """
        Get an attendance type by its name.
        
        Args:
            name: Attendance name
            
        Returns:
            Attendance ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            attendance = session.query(Attendance).filter(Attendance.Name == name).first()
            if attendance:
                session.expunge(attendance)
            return attendance
    
    def get_all(self) -> List[Attendance]:
        """
        Get all attendance types from the database.
        
        Returns:
            List of Attendance ORM objects
        """
        with self.db.session_scope() as session:
            attendances = session.query(Attendance).all()
            for attendance in attendances:
                session.expunge(attendance)
            return attendances
