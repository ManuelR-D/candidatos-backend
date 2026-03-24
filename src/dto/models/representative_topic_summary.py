"""RepresentativeTopicSummary ORM Model."""
from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database import Base


class RepresentativeTopicSummary(Base):
    """Summary per representative and topic."""

    __tablename__ = 'representativetopicsummary'

    UniqueID = Column('uniqueid', Integer, primary_key=True, autoincrement=True)
    Representative_id = Column('representative_id', UUID(as_uuid=True), ForeignKey('representative.uniqueid', ondelete='CASCADE'), nullable=False)
    Topic_id = Column('topic_id', Integer, ForeignKey('topic.uniqueid', ondelete='CASCADE'), nullable=False)
    Summary = Column('summary', Text, nullable=False)

    __table_args__ = (
        UniqueConstraint('representative_id', 'topic_id', name='uq_representative_topic_summary'),
    )

    representative = relationship("Representative", back_populates="topic_summaries")
    topic = relationship("Topic", back_populates="representative_summaries")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'representative_id': self.Representative_id,
            'topic_id': self.Topic_id,
            'summary': self.Summary
        }
