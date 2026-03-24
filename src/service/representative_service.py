"""Representative service for database operations using SQLAlchemy ORM."""
from typing import Optional, List, cast
from uuid import UUID
from src.service.postgres_service import PostgreService
from src.dto.models.representative import Representative


class RepresentativeService:
    """Service for managing Representative database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize RepresentativeService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, representative_data: dict) -> UUID:
        """
        Insert a representative into the database.
        
        Args:
            representative_data: Dictionary with representative data
            
        Returns:
            The UUID of the inserted representative
        """
        with self.db.session_scope() as session:
            representative = Representative(
                External_id=representative_data.get('external_id'),
                Full_name=representative_data['full_name'],
                Last_name=representative_data.get('last_name'),
                First_name=representative_data.get('first_name'),
                Province_id=representative_data['province_id'],
                Party_id=representative_data['party_id'],
                Coalition_id=representative_data.get('coalition_id'),
                Legal_start_date=representative_data.get('legal_start_date'),
                Legal_end_date=representative_data.get('legal_end_date'),
                Real_start_date=representative_data.get('real_start_date'),
                Real_end_date=representative_data.get('real_end_date'),
                Email=representative_data.get('email'),
                Phone=representative_data.get('phone'),
                Photo_url=representative_data.get('photo_url'),
                Facebook_url=representative_data.get('facebook_url'),
                Twitter_url=representative_data.get('twitter_url'),
                Instagram_url=representative_data.get('instagram_url'),
                Youtube_url=representative_data.get('youtube_url')
            )
            session.add(representative)
            session.flush()  # Flush to get the generated UUID
            return cast(UUID, representative.UniqueID)
    
    def insert_many(self, representatives_data: List[dict]) -> None:
        """
        Insert multiple representatives into the database.
        
        Args:
            representatives_data: List of dictionaries with representative data
        """
        with self.db.session_scope() as session:
            representatives = [
                Representative(
                    External_id=data.get('external_id'),
                    Full_name=data['full_name'],
                    Last_name=data.get('last_name'),
                    First_name=data.get('first_name'),
                    Province_id=data['province_id'],
                    Party_id=data['party_id'],
                    Coalition_id=data.get('coalition_id'),
                    Legal_start_date=data.get('legal_start_date'),
                    Legal_end_date=data.get('legal_end_date'),
                    Real_start_date=data.get('real_start_date'),
                    Real_end_date=data.get('real_end_date'),
                    Email=data.get('email'),
                    Phone=data.get('phone'),
                    Photo_url=data.get('photo_url'),
                    Facebook_url=data.get('facebook_url'),
                    Twitter_url=data.get('twitter_url'),
                    Instagram_url=data.get('instagram_url'),
                    Youtube_url=data.get('youtube_url')
                )
                for data in representatives_data
            ]
            session.add_all(representatives)
    
    def get_by_id(self, unique_id: UUID) -> Optional[Representative]:
        """
        Get a representative by their unique ID.
        
        Args:
            unique_id: Representative UUID
            
        Returns:
            Representative ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            representative = session.query(Representative).filter(
                Representative.UniqueID == unique_id
            ).first()
            if representative:
                session.expunge(representative)  # Detach from session
            return representative
    
    def get_by_external_id(self, external_id: str) -> Optional[Representative]:
        """
        Get a representative by their external ID.
        
        Args:
            external_id: Representative external ID
            
        Returns:
            Representative ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            representative = session.query(Representative).filter(
                Representative.External_id == external_id
            ).first()
            if representative:
                session.expunge(representative)  # Detach from session
            return representative
    
    def get_all(self) -> List[Representative]:
        """
        Get all representatives from the database.
        
        Returns:
            List of Representative ORM objects
        """
        with self.db.session_scope() as session:
            representatives = session.query(Representative).order_by(
                Representative.Last_name,
                Representative.First_name
            ).all()
            for rep in representatives:
                session.expunge(rep)  # Detach from session
            return representatives
