"""Session Representative Data Transfer Object."""
from dataclasses import dataclass


@dataclass
class SessionRepresentative:
    """Represents an attendee/representative at the session."""
    last_name: str
    first_name: str
    
    def full_name(self) -> str:
        """Returns the full name in 'LAST_NAME, First Name' format."""
        return f"{self.last_name}, {self.first_name}"
