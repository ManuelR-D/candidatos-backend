"""Service layer for SessionFile operations using SQLAlchemy ORM."""
from typing import Optional, List, cast
from datetime import datetime
from src.service.postgres_service import PostgreService
from src.dto.models.session_file import SessionFile


class SessionFileService:
    """Service for managing session file records using ORM."""
    
    def __init__(self, postgres_service: PostgreService):
        """
        Initialize the service.
        
        Args:
            postgres_service: PostgreService instance for database operations
        """
        self.db = postgres_service
    
    def create(self, senate_session_id: int, file_hash: str, file_name: str, 
               file_size: int, upload_date: datetime) -> int:
        """
        Create a new session file record.
        
        Args:
            senate_session_id: ID of the senate session
            file_hash: SHA-256 hash of the file
            file_name: Name of the file
            file_size: Size of the file in bytes
            upload_date: Upload timestamp
            
        Returns:
            The unique_id of the created record
        """
        with self.db.session_scope() as session:
            session_file = SessionFile(
                SenateSession_id=senate_session_id,
                File_hash=file_hash,
                File_name=file_name,
                File_size=file_size,
                Upload_date=upload_date
            )
            session.add(session_file)
            session.flush()
            return cast(int, session_file.UniqueID)
    
    def get_by_hash(self, file_hash: str) -> Optional[SessionFile]:
        """
        Get a session file by its hash.
        
        Args:
            file_hash: The SHA-256 hash of the file
            
        Returns:
            SessionFile object if found, None otherwise
        """
        with self.db.session_scope() as session:
            session_file = session.query(SessionFile).filter(
                SessionFile.File_hash == file_hash
            ).first()
            if session_file:
                session.expunge(session_file)
            return session_file
    
    def delete_by_hash(self, file_hash: str) -> bool:
        """
        Delete a session file record by hash.
        
        Args:
            file_hash: The SHA-256 hash of the file
            
        Returns:
            True if deleted, False otherwise
        """
        with self.db.session_scope() as session:
            result = session.query(SessionFile).filter(
                SessionFile.File_hash == file_hash
            ).delete()
            return result > 0
    
    def get_all(self) -> List[SessionFile]:
        """
        Get all session file records.
        
        Returns:
            List of SessionFile objects
        """
        with self.db.session_scope() as session:
            files = session.query(SessionFile).order_by(
                SessionFile.Upload_date.desc()
            ).all()
            for file in files:
                session.expunge(file)
            return files
