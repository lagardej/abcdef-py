"""Shared fixtures for d/ tests."""

from abcdef.d import AggregateId, AggregateRoot, Repository


class DummyAggregate(AggregateRoot):
    """Minimal concrete aggregate for testing AggregateRoot and Repository behaviour."""

    def __init__(self, aggregate_id: AggregateId, name: str = "") -> None:
        """Initialise with an aggregate_id and optional name."""
        super().__init__(aggregate_id)
        self.name = name


class DummyRepository(Repository[AggregateId, DummyAggregate]):
    """In-memory repository for testing the Repository abstraction."""

    def __init__(self) -> None:
        """Initialise the repository."""
        self._store: dict[str, DummyAggregate] = {}

    def save(self, aggregate: DummyAggregate) -> None:
        """Save a dummy aggregate."""
        self._store[str(aggregate.id)] = aggregate

    def get_by_id(self, aggregate_id: AggregateId) -> DummyAggregate | None:
        """Load a dummy aggregate by ID."""
        return self._store.get(str(aggregate_id))

    def delete(self, aggregate_id: AggregateId) -> None:
        """Delete a dummy aggregate."""
        self._store.pop(str(aggregate_id), None)

    def find_all(self) -> list[DummyAggregate]:
        """Load all dummy aggregates."""
        return list(self._store.values())


__all__ = [
    "DummyAggregate",
    "DummyRepository",
]
