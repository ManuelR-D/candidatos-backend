"""Province service for database operations using SQLAlchemy ORM."""
from typing import Optional, List
from src.service.postgres_service import PostgreService
from src.dto.models.province import Province


class ProvinceService:
    """Service for managing Province database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize ProvinceService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, name: str) -> int:
        """
        Insert a province into the database.
        
        Args:
            name: Province name
            
        Returns:
            The unique_id of the inserted province
        """
        with self.db.session_scope() as session:
            province = Province(Name=name)
            session.add(province)
            session.flush()
            return province.UniqueID
    
    def insert_many(self, names: List[str]) -> None:
        """
        Insert multiple provinces into the database.
        
        Args:
            names: List of province names
        """
        with self.db.session_scope() as session:
            provinces = [Province(Name=name) for name in names]
            session.add_all(provinces)
    
    def get_by_id(self, unique_id: int) -> Optional[Province]:
        """
        Get a province by its unique ID.
        
        Args:
            unique_id: Province unique ID
            
        Returns:
            Province ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            province = session.query(Province).filter(Province.UniqueID == unique_id).first()
            if province:
                session.expunge(province)
            return province
    
    def get_by_name(self, name: str) -> Optional[Province]:
        """
        Get a province by its name.
        
        Args:
            name: Province name
            
        Returns:
            Province ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            province = session.query(Province).filter(Province.Name == name).first()
            if province:
                session.expunge(province)
            return province
    
    def get_all(self) -> List[Province]:
        """
        Get all provinces from the database.
        
        Returns:
            List of Province ORM objects
        """
        with self.db.session_scope() as session:
            provinces = session.query(Province).order_by(Province.Name).all()
            for province in provinces:
                session.expunge(province)
            return provinces
