"""Session Topic Data Transfer Object."""
from dataclasses import dataclass
from typing import List
from .intervention import Intervention


@dataclass
class SessionTopic:
    """Represents a topic discussed in the session."""
    number: str
    title: str
    interventions: List[Intervention]
