"""DDD architecture markers.

Decorators that mark classes with DDD concepts: aggregates, value objects,
repositories, domain services, specifications, factories, and identifiers. Markers are
inherited by subclasses.
"""


def aggregate[T](cls: T) -> T:
    """Mark a class as an Aggregate Root.

    An Aggregate is an entity that maintains invariants, can be loaded and saved as a
    unit, and emits domain events.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as an aggregate.

    Returns:
        The class with __ddd_type__ = "aggregate" metadata.
    """
    cls.__ddd_type__ = "aggregate"  # type: ignore[attr-defined]
    return cls


def value_object[T](cls: T) -> T:
    """Mark a class as a Value Object.

    A Value Object is an immutable object defined by its attributes, with no identity
    of its own. It is compared by value, not identity.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a value object.

    Returns:
        The class with __ddd_type__ = "value_object" metadata.
    """
    cls.__ddd_type__ = "value_object"  # type: ignore[attr-defined]
    return cls


def repository[T](cls: T) -> T:
    """Mark a class as a Repository.

    A Repository abstracts persistence, making aggregates appear to be in memory. It
    loads and saves aggregates and provides query methods.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a repository.

    Returns:
        The class with __ddd_type__ = "repository" metadata.
    """
    cls.__ddd_type__ = "repository"  # type: ignore[attr-defined]
    return cls


def domain_service[T](cls: T) -> T:
    """Mark a class as a Domain Service.

    A Domain Service encapsulates business logic that doesn't naturally belong to any
    single Aggregate or Value Object.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a domain service.

    Returns:
        The class with __ddd_type__ = "domain_service" metadata.
    """
    cls.__ddd_type__ = "domain_service"  # type: ignore[attr-defined]
    return cls


def factory[T](cls: T) -> T:
    """Mark a class as a Factory.

    A Factory encapsulates complex object creation logic, ensuring that newly created
    objects maintain invariants.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a factory.

    Returns:
        The class with __ddd_type__ = "factory" metadata.
    """
    cls.__ddd_type__ = "factory"  # type: ignore[attr-defined]
    return cls


def identifier[T](cls: T) -> T:
    """Mark a class as an Identifier (Value Object).

    An Identifier is a value object that uniquely identifies an aggregate or entity.
    It is immutable and compared by value.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as an identifier.

    Returns:
        The class with __ddd_type__ = "identifier" metadata.
    """
    cls.__ddd_type__ = "identifier"  # type: ignore[attr-defined]
    return cls
