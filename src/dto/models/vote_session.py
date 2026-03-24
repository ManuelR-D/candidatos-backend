"""VoteSession ORM Model."""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class VoteSession(Base):
    """VoteSession ORM model for database operations."""
    
    __tablename__ = 'votesession'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Representative_id = Column('representative_id', UUID(as_uuid=True), ForeignKey('representative.uniqueid', ondelete='CASCADE'), nullable=False)
    SenateSession_id = Column('senatesession_id', Integer, ForeignKey('senatesession.uniqueid', ondelete='CASCADE'), nullable=False)
    Topic_id = Column('topic_id', Integer, ForeignKey('topic.uniqueid', ondelete='CASCADE'), nullable=False)
    Vote_id = Column('vote_id', Integer, ForeignKey('vote.uniqueid', ondelete='RESTRICT'), nullable=False)
    
    # Relationships
    representative = relationship("Representative", back_populates="vote_sessions")
    senate_session = relationship("SenateSession", back_populates="vote_sessions")
    topic = relationship("Topic", back_populates="vote_sessions")
    vote = relationship("Vote", back_populates="vote_sessions")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'representative_id': self.Representative_id,
            'senate_session_id': self.SenateSession_id,
            'topic_id': self.Topic_id,
            'vote_id': self.Vote_id
        }
