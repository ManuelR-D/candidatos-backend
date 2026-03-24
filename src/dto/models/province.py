"""Province ORM Model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class Province(Base):
    """Province ORM model for database operations."""
    
    __tablename__ = 'province'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Name = Column('name', String(255), nullable=False, unique=True)
    
    # Relationships
    representatives = relationship("Representative", back_populates="province")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'name': self.Name
        }
