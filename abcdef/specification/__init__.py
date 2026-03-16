"""specification -- Specification pattern for abcdef.

Provides the Specification ABC, combinators, and the @specification architecture
marker.
"""

from .specification import Specification, specification

__all__ = [
    "Specification",
    "specification",
]
