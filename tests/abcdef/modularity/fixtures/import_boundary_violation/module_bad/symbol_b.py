"""Public symbol of module B with illegal import."""

# Violation: importing from module_a's internal package
from module_a.internal.impl_a import ImplA


class SymbolB:
    """Public class that uses internal ImplA (boundary violation)."""

    def __init__(self) -> None:
        """Initialize SymbolB with internal ImplA (violation)."""
        self.impl = ImplA()
