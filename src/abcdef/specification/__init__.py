"""Composable business-rule predicates using the Specification pattern."""

from .markers import specification
from .specification import Specification

__all__ = [
    "Specification",
    "specification",
]
