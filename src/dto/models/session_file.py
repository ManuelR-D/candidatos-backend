"""SessionFile ORM model for tracking parsed session files."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


class SessionFile(Base):
    """SessionFile ORM model for database operations."""
    
    __tablename__ = 'sessionfile'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    SenateSession_id = Column('senatesession_id', Integer, ForeignKey('senatesession.uniqueid', ondelete='CASCADE'), nullable=False)
    File_hash = Column('file_hash', String(64), nullable=False, unique=True)
    File_name = Column('file_name', String(255), nullable=False)
    File_size = Column('file_size', Integer, nullable=False)
    Upload_date = Column('upload_date', DateTime, nullable=False, default=datetime.now)
    
    # Relationship
    senate_session = relationship("SenateSession", back_populates="session_files")
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'unique_id': self.UniqueID,
            'senate_session_id': self.SenateSession_id,
            'file_hash': self.File_hash,
            'file_name': self.File_name,
            'file_size': self.File_size,
            'upload_date': self.Upload_date.isoformat() if self.Upload_date else None
        }
