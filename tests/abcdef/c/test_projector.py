"""Tests for Projector abstraction."""

from __future__ import annotations

import datetime

import pytest

from abcdef.b import Event
from abcdef.c import Projector
from abcdef.c.markers import projector as projector_marker

_TS = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC)


class SomethingHappened(Event):
    """Dummy event for testing."""

    event_type = "something_happened"

    def __init__(self, value: str) -> None:
        """Initialise with a value."""
        super().__init__(occurred_at=_TS)
        object.__setattr__(self, "value", value)


class DummyProjector(Projector[SomethingHappened]):
    """Concrete projector that records projected events."""

    def __init__(self) -> None:
        """Initialise with an empty log."""
        self.log: list[SomethingHappened] = []

    def project(self, event: SomethingHappened) -> None:
        """Record the event."""
        self.log.append(event)


class TestProjectorABC:
    """Tests for Projector abstract base class."""

    def test_cannot_instantiate_without_project(self) -> None:
        """Projector cannot be instantiated without implementing project."""

        class IncompleteProjector(Projector[SomethingHappened]):
            pass

        with pytest.raises(TypeError):
            IncompleteProjector()  # type: ignore[abstract]

    def test_concrete_projector_can_be_instantiated(self) -> None:
        """A fully implemented Projector can be instantiated."""
        proj = DummyProjector()
        assert proj is not None

    def test_project_is_called_with_event(self) -> None:
        """project() receives the event and can act on it."""
        proj = DummyProjector()
        event = SomethingHappened("hello")

        proj.project(event)

        assert len(proj.log) == 1
        assert proj.log[0].value == "hello"  # type: ignore[attr-defined]

    def test_projector_marker_on_abc(self) -> None:
        """Projector ABC carries the projector marker."""
        assert projector_marker.__name__ == "projector"
        assert Projector.__cqrs_type__ == "projector"  # type: ignore[attr-defined]

    def test_projector_marker_inherited_by_subclass(self) -> None:
        """Concrete subclass inherits the projector marker."""
        assert DummyProjector.__cqrs_type__ == "projector"  # type: ignore[attr-defined]
