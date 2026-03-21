"""SymbolA — exported from module_a."""

from ..shared.helpers.utility import shared_utility


class SymbolA:
    """A symbol exported from module_a (defined at root level)."""

    def __init__(self) -> None:
        """Initialize SymbolA."""
        self.value = "A"
        self.shared = shared_utility()
