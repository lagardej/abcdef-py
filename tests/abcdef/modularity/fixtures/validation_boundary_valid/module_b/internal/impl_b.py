"""Implementation file (internal, not exported)."""

from ...shared.helpers.utility import shared_utility


class HelperB:
    """Helper class that uses shared utility (internal to module_b)."""

    def __init__(self) -> None:
        """Initialize HelperB."""
        self.utility_result = shared_utility()
