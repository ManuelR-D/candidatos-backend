"""SenateSession ORM Model."""
from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class SenateSession(Base):
    """SenateSession ORM model for database operations."""
    
    __tablename__ = 'senatesession'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Date = Column('date', Date, nullable=False)
    Session_type_id = Column('session_type_id', Integer, ForeignKey('sessiontype.uniqueid', ondelete='RESTRICT'))
    
    # Relationships
    session_type = relationship("SessionType", back_populates="senate_sessions")
    topics = relationship("Topic", back_populates="senate_session", cascade="all, delete-orphan")
    attendance_sessions = relationship("AttendanceSession", back_populates="senate_session", cascade="all, delete-orphan")
    vote_sessions = relationship("VoteSession", back_populates="senate_session", cascade="all, delete-orphan")
    session_files = relationship("SessionFile", back_populates="senate_session", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'date': self.Date
        }
