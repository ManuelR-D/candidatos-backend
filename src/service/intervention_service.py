"""Intervention service for database operations using SQLAlchemy ORM."""
from typing import Optional, List, cast
from uuid import UUID
from src.service.postgres_service import PostgreService
from src.dto.models.intervention import Intervention


class InterventionService:
    """Service for managing Intervention database operations using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize InterventionService.
        
        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service
    
    def insert(self, topic_id: int, representative_id: UUID, text: str, role: Optional[str] = None, 
               intervention_order: Optional[int] = None) -> int:
        """
        Insert an intervention into the database.
        
        Args:
            topic_id: Topic ID
            representative_id: Representative UUID
            text: Intervention text
            role: Representative role (optional)
            intervention_order: Order of intervention (optional)
            
        Returns:
            The unique_id of the inserted intervention
        """
        with self.db.session_scope() as session:
            intervention = Intervention(
                Topic_id=topic_id,
                Representative_id=representative_id,
                Text=text,
                Role=role,
                Intervention_order=intervention_order
            )
            session.add(intervention)
            session.flush()
            return cast(int, intervention.UniqueID)
    
    def insert_many(self, interventions_data: List[dict]) -> None:
        """
        Insert multiple interventions into the database.
        
        Args:
            interventions_data: List of dictionaries with intervention data
        """
        with self.db.session_scope() as session:
            interventions = [
                Intervention(
                    Topic_id=data['topic_id'],
                    Representative_id=data['representative_id'],
                    Text=data['text'],
                    Role=data.get('role'),
                    Intervention_order=data.get('intervention_order')
                )
                for data in interventions_data
            ]
            session.add_all(interventions)
    
    def get_by_id(self, unique_id: int) -> Optional[Intervention]:
        """
        Get an intervention by its unique ID.
        
        Args:
            unique_id: Intervention unique ID
            
        Returns:
            Intervention ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            intervention = session.query(Intervention).filter(
                Intervention.UniqueID == unique_id
            ).first()
            if intervention:
                session.expunge(intervention)
            return intervention
    
    def get_by_topic(self, topic_id: int) -> List[Intervention]:
        """
        Get all interventions for a specific topic.
        
        Args:
            topic_id: Topic unique ID
            
        Returns:
            List of Intervention ORM objects ordered by intervention_order
        """
        with self.db.session_scope() as session:
            interventions = session.query(Intervention).filter(
                Intervention.Topic_id == topic_id
            ).order_by(Intervention.Intervention_order).all()
            for intervention in interventions:
                session.expunge(intervention)
            return interventions
    
    def get_by_representative(self, representative_id: UUID) -> List[Intervention]:
        """
        Get all interventions by a specific representative.
        
        Args:
            representative_id: Representative UUID
            
        Returns:
            List of Intervention ORM objects
        """
        with self.db.session_scope() as session:
            interventions = session.query(Intervention).filter(
                Intervention.Representative_id == representative_id
            ).order_by(Intervention.Topic_id, Intervention.Intervention_order).all()
            for intervention in interventions:
                session.expunge(intervention)
            return interventions

    def get_by_topic_and_representative(self, topic_id: int, representative_id: UUID) -> List[Intervention]:
        """
        Get all interventions for a specific topic.
        
        Args:
            topic_id: Topic unique ID
            representative_id: Representative UUID

        Returns:
            List of Intervention ORM objects ordered by intervention_order and filtered by representative
        """
        with self.db.session_scope() as session:
            interventions = session.query(Intervention).filter(
                Intervention.Topic_id == topic_id
            ).order_by(Intervention.Intervention_order).filter(
                Intervention.Representative_id == representative_id
            ).all()
            for intervention in interventions:
                session.expunge(intervention)
            return interventions