"""Implementation file (internal, not exported)."""

from ...shared.helpers.utility import shared_utility


class HelperA:
    """Helper class that uses shared utility (internal to module_a)."""

    def __init__(self) -> None:
        """Initialize HelperA."""
        self.utility_result = shared_utility()
