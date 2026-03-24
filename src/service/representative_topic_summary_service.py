"""RepresentativeTopicSummary service for database operations using SQLAlchemy ORM."""
from typing import Optional, cast
from uuid import UUID
from src.service.postgres_service import PostgreService
from src.dto.models.representative_topic_summary import RepresentativeTopicSummary


class RepresentativeTopicSummaryService:
    """Service for managing RepresentativeTopicSummary database operations using ORM."""

    def __init__(self, postgres_service: PostgreService):
        """
        Initialize RepresentativeTopicSummaryService.

        Args:
            postgres_service: PostgreSQL service instance
        """
        self.db = postgres_service

    def upsert(self, representative_id: UUID, topic_id: int, summary: str) -> int:
        """
        Insert or update a representative-topic summary.

        Args:
            representative_id: Representative UUID
            topic_id: Topic ID
            summary: Summary text

        Returns:
            The unique_id of the summary record
        """
        with self.db.session_scope() as session:
            existing = session.query(RepresentativeTopicSummary).filter(
                RepresentativeTopicSummary.Representative_id == representative_id,
                RepresentativeTopicSummary.Topic_id == topic_id
            ).first()
            if existing:
                existing.Summary = summary
                session.flush()
                return cast(int, existing.UniqueID)

            item = RepresentativeTopicSummary(
                Representative_id=representative_id,
                Topic_id=topic_id,
                Summary=summary
            )
            session.add(item)
            session.flush()
            return cast(int, item.UniqueID)

    def get_by_representative_and_topic(self, representative_id: UUID, topic_id: int) -> Optional[RepresentativeTopicSummary]:
        """
        Get a summary by representative and topic.

        Args:
            representative_id: Representative UUID
            topic_id: Topic ID

        Returns:
            RepresentativeTopicSummary ORM object if found, None otherwise
        """
        with self.db.session_scope() as session:
            summary = session.query(RepresentativeTopicSummary).filter(
                RepresentativeTopicSummary.Representative_id == representative_id,
                RepresentativeTopicSummary.Topic_id == topic_id
            ).first()
            if summary:
                session.expunge(summary)
            return summary
