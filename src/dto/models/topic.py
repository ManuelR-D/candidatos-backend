"""Topic ORM Model."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class Topic(Base):
    """Topic ORM model for database operations."""
    
    __tablename__ = 'topic'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    SenateSession_id = Column('senatesession_id', Integer, ForeignKey('senatesession.uniqueid', ondelete='CASCADE'), nullable=False)
    Name = Column('name', Text, nullable=False)
    
    # Relationships
    senate_session = relationship("SenateSession", back_populates="topics")
    interventions = relationship("Intervention", back_populates="topic", cascade="all, delete-orphan")
    representative_summaries = relationship("RepresentativeTopicSummary", back_populates="topic", cascade="all, delete-orphan")
    vote_sessions = relationship("VoteSession", back_populates="topic", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'senate_session_id': self.SenateSession_id,
            'name': self.Name
        }
