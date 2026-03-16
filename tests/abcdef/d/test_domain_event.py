"""Tests for Event, DomainEvent, and DomainEventRegistry."""

from __future__ import annotations

import datetime

import pytest

from abcdef.core import Event
from abcdef.d import DomainEvent, DomainEventRegistry

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TS = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC)


class ConcreteEvent(Event):
    """Minimal concrete Event for testing."""

    event_type = "concrete_event"

    def __init__(self) -> None:
        """Initialise."""
        super().__init__(occurred_at=_TS)


class ConcreteDomainEvent(DomainEvent):
    """Minimal concrete DomainEvent for testing."""

    event_type = "concrete_domain_event"

    def __init__(self) -> None:
        """Initialise."""
        super().__init__(occurred_at=_TS)


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------


class TestEvent:
    """Tests for the Event base class."""

    def test_occurred_at_is_stored(self) -> None:
        """occurred_at is accessible on the instance."""
        assert ConcreteEvent().occurred_at == _TS

    def test_event_type_classvar_is_accessible(self) -> None:
        """event_type is readable from both the class and an instance."""
        assert ConcreteEvent.event_type == "concrete_event"
        assert ConcreteEvent().event_type == "concrete_event"

    def test_missing_event_type_raises_on_class_definition(self) -> None:
        """Defining a concrete subclass without event_type raises TypeError."""
        with pytest.raises(TypeError, match="event_type"):

            class BadEvent(Event):
                def __init__(self) -> None:
                    super().__init__(occurred_at=_TS)

    def test_empty_event_type_raises_on_class_definition(self) -> None:
        """Defining a concrete subclass with event_type = '' raises TypeError."""
        with pytest.raises(TypeError, match="event_type"):

            class EmptyTypeEvent(Event):
                event_type = ""

                def __init__(self) -> None:
                    super().__init__(occurred_at=_TS)

    def test_abstract_event_flag_exempts_intermediate_base(self) -> None:
        """A subclass with _abstract_event = True is exempt from the check."""

        class IntermediateBase(Event):
            _abstract_event = True

        assert IntermediateBase  # no TypeError raised

    def test_concrete_subclass_of_intermediate_must_define_event_type(
        self,
    ) -> None:
        """Concrete subclass of an intermediate base must define event_type."""

        class IntermediateBase(Event):
            _abstract_event = True

        with pytest.raises(TypeError, match="event_type"):

            class ConcreteWithoutType(IntermediateBase):
                def __init__(self) -> None:
                    super().__init__(occurred_at=_TS)

    def test_event_type_not_inherited_without_override(self) -> None:
        """A subclass cannot inherit event_type to satisfy the check."""
        with pytest.raises(TypeError, match="event_type"):

            class InheritedTypeEvent(ConcreteEvent):
                def __init__(self) -> None:
                    super().__init__()

    def test_occurred_at_is_immutable(self) -> None:
        """Assigning to occurred_at after construction raises AttributeError."""
        event = ConcreteEvent()
        with pytest.raises(AttributeError):
            event.occurred_at = _TS  # type: ignore[misc]

    def test_new_attribute_cannot_be_set(self) -> None:
        """Setting an arbitrary attribute after construction raises."""
        event = ConcreteEvent()
        with pytest.raises(AttributeError):
            event.new_field = "x"  # type: ignore[attr-defined]

    def test_attribute_cannot_be_deleted(self) -> None:
        """Deleting an attribute after construction raises AttributeError."""
        event = ConcreteEvent()
        with pytest.raises(AttributeError):
            del event.occurred_at  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DomainEvent
# ---------------------------------------------------------------------------


class TestDomainEvent:
    """Tests for DomainEvent."""

    def test_is_event(self) -> None:
        """DomainEvent is a subtype of Event."""
        assert isinstance(ConcreteDomainEvent(), Event)

    def test_occurred_at_is_stored(self) -> None:
        """occurred_at is inherited and accessible."""
        assert ConcreteDomainEvent().occurred_at == _TS

    def test_missing_event_type_raises(self) -> None:
        """Concrete DomainEvent subclass without event_type raises TypeError."""
        with pytest.raises(TypeError, match="event_type"):

            class BadDomainEvent(DomainEvent):
                def __init__(self) -> None:
                    super().__init__(occurred_at=_TS)

    def test_immutable(self) -> None:
        """Assigning an attribute after construction raises AttributeError."""
        event = ConcreteDomainEvent()
        with pytest.raises(AttributeError):
            event.occurred_at = _TS  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DomainEventRegistry
# ---------------------------------------------------------------------------


class TestDomainEventRegistry:
    """Tests for DomainEventRegistry."""

    def test_register_and_get(self) -> None:
        """A registered class is retrievable by event_type."""
        registry = DomainEventRegistry()
        registry.register(ConcreteDomainEvent.event_type, ConcreteDomainEvent)
        assert registry.get(ConcreteDomainEvent.event_type) is ConcreteDomainEvent

    def test_get_unknown_event_type_raises(self) -> None:
        """Looking up an unregistered event_type raises KeyError."""
        registry = DomainEventRegistry()
        with pytest.raises(KeyError):
            registry.get("no_such_event_type")

    def test_duplicate_event_type_raises(self) -> None:
        """Registering the same event_type twice raises TypeError."""
        registry = DomainEventRegistry()
        registry.register(ConcreteDomainEvent.event_type, ConcreteDomainEvent)
        with pytest.raises(TypeError, match="already registered"):
            registry.register(ConcreteDomainEvent.event_type, ConcreteDomainEvent)

    def test_each_instance_is_independent(self) -> None:
        """Two registry instances do not share state."""
        r1 = DomainEventRegistry()
        r2 = DomainEventRegistry()
        r1.register(ConcreteDomainEvent.event_type, ConcreteDomainEvent)
        with pytest.raises(KeyError):
            r2.get(ConcreteDomainEvent.event_type)
