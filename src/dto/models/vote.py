"""Vote ORM Model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class Vote(Base):
    """Vote ORM model for database operations."""
    
    __tablename__ = 'vote'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Name = Column('name', String(100), nullable=False)
    
    # Relationships
    vote_sessions = relationship("VoteSession", back_populates="vote")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'name': self.Name
        }
