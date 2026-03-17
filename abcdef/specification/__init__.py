"""specification -- Specification pattern for abcdef.

Provides the Specification ABC, combinators, and the @specification architecture
marker.
"""

from .markers import specification
from .specification import Specification

__all__ = [
    "Specification",
    "specification",
]
