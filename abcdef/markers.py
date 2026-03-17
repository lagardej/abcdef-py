"""Shared marker inspection utility.

Provides runtime inspection of architecture markers applied by the c/, d/, de/,
and specification/ marker modules.

Marker attribute convention:
- c/             uses ``__cqrs_type__``
- d/             uses ``__ddd_type__``
- de/            uses ``__de_type__``
- specification/ uses ``__specification_type__``
"""

from typing import cast


def _get_marker(cls: type, marker_attr: str) -> str | None:
    """Get marker value from class or its parents.

    Args:
        cls: The class to inspect.
        marker_attr: The marker attribute name (``__cqrs_type__``, ``__ddd_type__``,
            ``__de_type__``, or ``__specification_type__``).

    Returns:
        The marker value if found on the class or any base class, None otherwise.
    """
    value = getattr(cls, marker_attr, None)
    return cast("str", value) if value is not None else None
