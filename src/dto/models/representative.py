"""Representative ORM Model."""
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.database import Base


class Representative(Base):
    """Representative ORM model for database operations."""
    
    __tablename__ = 'representative'
    
    UniqueID = Column('uniqueid', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    External_id = Column('external_id', String(50))
    Full_name = Column('full_name', String(255), nullable=False)
    Last_name = Column('last_name', String(255))
    First_name = Column('first_name', String(255))
    Province_id = Column('province_id', Integer, ForeignKey('province.uniqueid', ondelete='RESTRICT'), nullable=False)
    Party_id = Column('party_id', Integer, ForeignKey('party.uniqueid', ondelete='RESTRICT'), nullable=False)
    Coalition_id = Column('coalition_id', Integer, ForeignKey('coalition.uniqueid', ondelete='SET NULL'))
    Legal_start_date = Column('legal_start_date', Date)
    Legal_end_date = Column('legal_end_date', Date)
    Real_start_date = Column('real_start_date', Date)
    Real_end_date = Column('real_end_date', String(50))
    Email = Column('email', String(255))
    Phone = Column('phone', String(100))
    Photo_url = Column('photo_url', Text)
    Facebook_url = Column('facebook_url', Text)
    Twitter_url = Column('twitter_url', Text)
    Instagram_url = Column('instagram_url', Text)
    Youtube_url = Column('youtube_url', Text)
    
    # Relationships
    province = relationship("Province", back_populates="representatives")
    party = relationship("Party", back_populates="representatives")
    coalition = relationship("Coalition", back_populates="representatives")
    interventions = relationship("Intervention", back_populates="representative", cascade="all, delete-orphan")
    topic_summaries = relationship("RepresentativeTopicSummary", back_populates="representative", cascade="all, delete-orphan")
    attendance_sessions = relationship("AttendanceSession", back_populates="representative", cascade="all, delete-orphan")
    vote_sessions = relationship("VoteSession", back_populates="representative", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'unique_id': self.UniqueID,
            'external_id': self.External_id,
            'full_name': self.Full_name,
            'last_name': self.Last_name,
            'first_name': self.First_name,
            'province_id': self.Province_id,
            'party_id': self.Party_id,
            'coalition_id': self.Coalition_id,
            'legal_start_date': self.Legal_start_date,
            'legal_end_date': self.Legal_end_date,
            'real_start_date': self.Real_start_date,
            'real_end_date': self.Real_end_date,
            'email': self.Email,
            'phone': self.Phone,
            'photo_url': self.Photo_url,
            'facebook_url': self.Facebook_url,
            'twitter_url': self.Twitter_url,
            'instagram_url': self.Instagram_url,
            'youtube_url': self.Youtube_url
        }
