"""Coalition ORM Model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class Coalition(Base):
    """Coalition ORM model for database operations."""
    
    __tablename__ = 'coalition'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Name = Column('name', String(255), nullable=False, unique=True)
    
    # Relationships
    representatives = relationship("Representative", back_populates="coalition")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'name': self.Name
        }
