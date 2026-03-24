"""File utility functions."""
import hashlib
import re
from typing import Optional
from datetime import datetime


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 hash as hexadecimal string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def parse_session_filename(filename: str) -> tuple[Optional[datetime], Optional[str]]:
        """Parse session date and type from filename.
        
        Expected format: VT-DD-MM-YYYY-ST-XX
        where ST is the session type short name (e.g., OR, EX, AS)
        
        Args:
            filename: The filename to parse
            
        Returns:
            Tuple of (date, session_type_short_name) or (None, None) if parsing fails
        """
        # Pattern: VT-DD-MM-YYYY-ST-XX
        pattern = r'^VT-(\d{2})-(\d{2})-(\d{4})-([A-Z]{2})-\d+'
        match = re.match(pattern, filename)
        
        if match:
            day, month, year, session_type = match.groups()
            try:
                parsed_date = datetime(int(year), int(month), int(day))
                return parsed_date, session_type
            except ValueError:
                return None, None
        
        return None, None
