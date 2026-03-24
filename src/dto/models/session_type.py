"""SessionType ORM Model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class SessionType(Base):
    """SessionType ORM model for database operations."""
    
    __tablename__ = 'sessiontype'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Name = Column('name', String(100), nullable=False)
    Short_name = Column('short_name', String(10), nullable=False)
    
    # Relationships
    senate_sessions = relationship("SenateSession", back_populates="session_type")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'name': self.Name,
            'short_name': self.Short_name
        }
