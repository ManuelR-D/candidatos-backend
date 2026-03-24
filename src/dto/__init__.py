"""DTO module exports."""
from .intervention import Intervention
from .session_topic import SessionTopic
from .session_representative import SessionRepresentative

# Keep backward compatibility by aliasing
Topic = SessionTopic
Representative = SessionRepresentative

__all__ = ['Intervention', 'SessionTopic', 'SessionRepresentative', 'Topic', 'Representative']
