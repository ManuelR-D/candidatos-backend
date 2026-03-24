"""AttendanceSession ORM Model."""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class AttendanceSession(Base):
    """AttendanceSession ORM model for database operations."""
    
    __tablename__ = 'attendancesession'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Representative_id = Column('representative_id', UUID(as_uuid=True), ForeignKey('representative.uniqueid', ondelete='CASCADE'), nullable=False)
    SenateSession_id = Column('senatesession_id', Integer, ForeignKey('senatesession.uniqueid', ondelete='CASCADE'), nullable=False)
    Attendance_id = Column('attendance_id', Integer, ForeignKey('attendance.uniqueid', ondelete='RESTRICT'), nullable=False)
    
    # Relationships
    representative = relationship("Representative", back_populates="attendance_sessions")
    senate_session = relationship("SenateSession", back_populates="attendance_sessions")
    attendance = relationship("Attendance", back_populates="attendance_sessions")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'representative_id': self.Representative_id,
            'senate_session_id': self.SenateSession_id,
            'attendance_id': self.Attendance_id
        }
