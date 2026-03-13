"""cde — CQRS + DDD + Event Sourcing intersection.

Contains concepts that belong simultaneously to all three paradigms.
Currently: the Event base class and its marker.
"""

from .event import Event
from .markers import event

__all__ = [
    "Event",
    "event",
]
