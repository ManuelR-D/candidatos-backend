"""Attendance ORM Model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class Attendance(Base):
    """Attendance ORM model for database operations."""
    
    __tablename__ = 'attendance'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Name = Column('name', String(100), nullable=False)
    
    # Relationships
    attendance_sessions = relationship("AttendanceSession", back_populates="attendance")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'name': self.Name
        }
