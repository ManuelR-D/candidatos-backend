"""Intervention ORM Model."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import Text as TextType
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class Intervention(Base):
    """Intervention ORM model for database operations."""
    
    __tablename__ = 'intervention'
    
    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Topic_id = Column('topic_id', Integer, ForeignKey('topic.uniqueid', ondelete='CASCADE'), nullable=False)
    Representative_id = Column('representative_id', UUID(as_uuid=True), ForeignKey('representative.uniqueid', ondelete='CASCADE'), nullable=False)
    Text = Column('text', TextType, nullable=False)
    Role = Column('role', String(100))
    Intervention_order = Column('intervention_order', Integer)
    
    # Relationships
    topic = relationship("Topic", back_populates="interventions")
    representative = relationship("Representative", back_populates="interventions")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'topic_id': self.Topic_id,
            'representative_id': self.Representative_id,
            'text': self.Text,
            'role': self.Role,
            'intervention_order': self.Intervention_order
        }
