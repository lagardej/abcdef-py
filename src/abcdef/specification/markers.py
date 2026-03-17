"""Specification architecture markers.

Decorators that mark classes with the Specification pattern concept. Markers are
inherited by subclasses.

Marker attribute convention:
- specification/ uses ``__specification_type__``
"""


def specification[T](cls: T) -> T:
    """Mark a class as a Specification.

    A Specification encapsulates a single business rule as a reusable, composable
    predicate. It has no dependency on DDD, CQRS, or event sourcing.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a specification.

    Returns:
        The class with ``__specification_type__ = "specification"`` metadata.
    """
    cls.__specification_type__ = "specification"  # type: ignore[attr-defined]
    return cls
