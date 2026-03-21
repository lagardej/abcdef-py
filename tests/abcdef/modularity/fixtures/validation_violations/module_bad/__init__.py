"""Module B — violates import boundary."""

from .symbol_b import SymbolB

__modularity__ = {"type": "query"}

__all__ = ["SymbolB"]
