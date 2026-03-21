"""Bad module that exports an internal implementation."""

from .internal.impl import InternalThing

__modularity__ = {"type": "command"}

# Violation: exporting internal symbol in __all__
__all__ = ["InternalThing"]
