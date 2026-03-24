"""Party ORM Model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class Party(Base):
    """Party ORM model for database operations."""
    
    __tablename__ = 'party'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Name = Column('name', String(255), nullable=False, unique=True)
    
    # Relationships
    representatives = relationship("Representative", back_populates="party")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'name': self.Name
        }
