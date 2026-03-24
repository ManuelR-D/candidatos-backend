"""Intervention Data Transfer Object."""
from dataclasses import dataclass
from .session_representative import SessionRepresentative


@dataclass
class Intervention:
    """Represents a single intervention/speech by a person during a session."""
    speaker: SessionRepresentative
    role: str
    text: str
