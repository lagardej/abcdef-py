"""Tests for architecture marker decorators and _get_marker inspection utility."""

from abcdef.c.markers import (
    command,
    command_handler,
    document,
    document_store,
    projector,
    query,
    query_handler,
)
from abcdef.d.markers import (
    aggregate,
    domain_service,
    factory,
    identifier,
    repository,
    value_object,
)
from abcdef.de.markers import aggregate_store, event_store
from abcdef.modularity.extraction import _get_marker

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _Bare:
    """Unmarked class for use as a decoration target."""

    pass


# ---------------------------------------------------------------------------
# _get_marker
# ---------------------------------------------------------------------------


class TestGetMarker:
    """Tests for _get_marker inspection utility."""

    def test_returns_marker_value_when_present(self) -> None:
        """Returns the marker value when the attribute exists on the class."""

        class Marked:
            __cqrs_type__ = "command"

        assert _get_marker(Marked, "__cqrs_type__") == "command"

    def test_returns_none_when_marker_absent(self) -> None:
        """Returns None when the marker attribute is not present."""

        class Unmarked:
            pass

        assert _get_marker(Unmarked, "__cqrs_type__") is None

    def test_returns_marker_from_parent(self) -> None:
        """Returns the marker value inherited from a parent class."""

        class Parent:
            __ddd_type__ = "aggregate"

        class Child(Parent):
            pass

        assert _get_marker(Child, "__ddd_type__") == "aggregate"

    def test_returns_none_for_unrelated_attribute(self) -> None:
        """Returns None when querying a marker attribute that was never set."""

        class Marked:
            __cqrs_type__ = "command"

        assert _get_marker(Marked, "__ddd_type__") is None

    def test_child_marker_takes_precedence_over_parent(self) -> None:
        """Returns the child's own marker value, not the parent's."""

        class Parent:
            __ddd_type__ = "aggregate"

        class Child(Parent):
            __ddd_type__ = "repository"

        assert _get_marker(Child, "__ddd_type__") == "repository"


# ---------------------------------------------------------------------------
# c/ markers
# ---------------------------------------------------------------------------


class TestCqrsMarkers:
    """Tests for CQRS marker decorators."""

    def test_command_returns_class_unchanged(self) -> None:
        """@command returns the decorated class itself."""
        cls = type("Cmd", (), {})
        result = command(cls)
        assert result is cls

    def test_command_sets_cqrs_type(self) -> None:
        """@command sets __cqrs_type__ to 'command'."""
        cls = type("Cmd", (), {})
        command(cls)
        assert cls.__cqrs_type__ == "command"  # type: ignore[attr-defined]

    def test_command_handler_returns_class_unchanged(self) -> None:
        """@command_handler returns the decorated class itself."""
        cls = type("Handler", (), {})
        result = command_handler(cls)
        assert result is cls

    def test_command_handler_sets_cqrs_type(self) -> None:
        """@command_handler sets __cqrs_type__ to 'command_handler'."""
        cls = type("Handler", (), {})
        command_handler(cls)
        assert cls.__cqrs_type__ == "command_handler"  # type: ignore[attr-defined]

    def test_query_returns_class_unchanged(self) -> None:
        """@query returns the decorated class itself."""
        cls = type("Qry", (), {})
        result = query(cls)
        assert result is cls

    def test_query_sets_cqrs_type(self) -> None:
        """@query sets __cqrs_type__ to 'query'."""
        cls = type("Qry", (), {})
        query(cls)
        assert cls.__cqrs_type__ == "query"  # type: ignore[attr-defined]

    def test_query_handler_returns_class_unchanged(self) -> None:
        """@query_handler returns the decorated class itself."""
        cls = type("QryHandler", (), {})
        result = query_handler(cls)
        assert result is cls

    def test_query_handler_sets_cqrs_type(self) -> None:
        """@query_handler sets __cqrs_type__ to 'query_handler'."""
        cls = type("QryHandler", (), {})
        query_handler(cls)
        assert cls.__cqrs_type__ == "query_handler"  # type: ignore[attr-defined]

    def test_document_returns_class_unchanged(self) -> None:
        """@document returns the decorated class itself."""
        cls = type("Doc", (), {})
        result = document(cls)
        assert result is cls

    def test_document_sets_cqrs_type(self) -> None:
        """@document sets __cqrs_type__ to 'document'."""
        cls = type("Doc", (), {})
        document(cls)
        assert cls.__cqrs_type__ == "document"  # type: ignore[attr-defined]

    def test_document_store_returns_class_unchanged(self) -> None:
        """@document_store returns the decorated class itself."""
        cls = type("DocStore", (), {})
        result = document_store(cls)
        assert result is cls

    def test_document_store_sets_cqrs_type(self) -> None:
        """@document_store sets __cqrs_type__ to 'document_store'."""
        cls = type("DocStore", (), {})
        document_store(cls)
        assert cls.__cqrs_type__ == "document_store"  # type: ignore[attr-defined]

    def test_projector_returns_class_unchanged(self) -> None:
        """@projector returns the decorated class itself."""
        cls = type("Proj", (), {})
        result = projector(cls)
        assert result is cls

    def test_projector_sets_cqrs_type(self) -> None:
        """@projector sets __cqrs_type__ to 'projector'."""
        cls = type("Proj", (), {})
        projector(cls)
        assert cls.__cqrs_type__ == "projector"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# d/ markers
# ---------------------------------------------------------------------------


class TestDddMarkers:
    """Tests for DDD marker decorators."""

    def test_aggregate_returns_class_unchanged(self) -> None:
        """@aggregate returns the decorated class itself."""
        cls = type("Agg", (), {})
        result = aggregate(cls)
        assert result is cls

    def test_aggregate_sets_ddd_type(self) -> None:
        """@aggregate sets __ddd_type__ to 'aggregate'."""
        cls = type("Agg", (), {})
        aggregate(cls)
        assert cls.__ddd_type__ == "aggregate"  # type: ignore[attr-defined]

    def test_value_object_returns_class_unchanged(self) -> None:
        """@value_object returns the decorated class itself."""
        cls = type("VO", (), {})
        result = value_object(cls)
        assert result is cls

    def test_value_object_sets_ddd_type(self) -> None:
        """@value_object sets __ddd_type__ to 'value_object'."""
        cls = type("VO", (), {})
        value_object(cls)
        assert cls.__ddd_type__ == "value_object"  # type: ignore[attr-defined]

    def test_repository_returns_class_unchanged(self) -> None:
        """@repository returns the decorated class itself."""
        cls = type("Repo", (), {})
        result = repository(cls)
        assert result is cls

    def test_repository_sets_ddd_type(self) -> None:
        """@repository sets __ddd_type__ to 'repository'."""
        cls = type("Repo", (), {})
        repository(cls)
        assert cls.__ddd_type__ == "repository"  # type: ignore[attr-defined]

    def test_domain_service_returns_class_unchanged(self) -> None:
        """@domain_service returns the decorated class itself."""
        cls = type("Svc", (), {})
        result = domain_service(cls)
        assert result is cls

    def test_domain_service_sets_ddd_type(self) -> None:
        """@domain_service sets __ddd_type__ to 'domain_service'."""
        cls = type("Svc", (), {})
        domain_service(cls)
        assert cls.__ddd_type__ == "domain_service"  # type: ignore[attr-defined]

    def test_factory_returns_class_unchanged(self) -> None:
        """@factory returns the decorated class itself."""
        cls = type("Fac", (), {})
        result = factory(cls)
        assert result is cls

    def test_factory_sets_ddd_type(self) -> None:
        """@factory sets __ddd_type__ to 'factory'."""
        cls = type("Fac", (), {})
        factory(cls)
        assert cls.__ddd_type__ == "factory"  # type: ignore[attr-defined]

    def test_identifier_returns_class_unchanged(self) -> None:
        """@identifier returns the decorated class itself."""
        cls = type("Id", (), {})
        result = identifier(cls)
        assert result is cls

    def test_identifier_sets_ddd_type(self) -> None:
        """@identifier sets __ddd_type__ to 'identifier'."""
        cls = type("Id", (), {})
        identifier(cls)
        assert cls.__ddd_type__ == "identifier"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# de/ markers
# ---------------------------------------------------------------------------


class TestEsMarkers:
    """Tests for Event Sourcing marker decorators."""

    def test_event_store_returns_class_unchanged(self) -> None:
        """@event_store returns the decorated class itself."""
        cls = type("ES", (), {})
        result = event_store(cls)
        assert result is cls

    def test_event_store_sets_de_type(self) -> None:
        """@event_store sets __de_type__ to 'event_store'."""
        cls = type("ES", (), {})
        event_store(cls)
        assert cls.__de_type__ == "event_store"  # type: ignore[attr-defined]

    def test_event_store_marker_visible_on_subclass(self) -> None:
        """@event_store marker is inherited by subclasses."""

        @event_store
        class BaseES:
            pass

        class SubES(BaseES):
            pass

        assert _get_marker(SubES, "__de_type__") == "event_store"

    def test_aggregate_store_returns_class_unchanged(self) -> None:
        """@aggregate_store returns the decorated class itself."""
        cls = type("AS", (), {})
        result = aggregate_store(cls)
        assert result is cls

    def test_aggregate_store_sets_de_type(self) -> None:
        """@aggregate_store sets __de_type__ to 'aggregate_store'."""
        cls = type("AS", (), {})
        aggregate_store(cls)
        assert cls.__de_type__ == "aggregate_store"  # type: ignore[attr-defined]

    def test_aggregate_store_marker_visible_on_subclass(self) -> None:
        """@aggregate_store marker is inherited by subclasses."""

        @aggregate_store
        class BaseAS:
            pass

        class SubAS(BaseAS):
            pass

        assert _get_marker(SubAS, "__de_type__") == "aggregate_store"


# ---------------------------------------------------------------------------
# Marker inheritance
# ---------------------------------------------------------------------------


class TestMarkerInheritance:
    """Tests that markers are visible on subclasses via _get_marker."""

    def test_cqrs_marker_visible_on_subclass(self) -> None:
        """A CQRS marker set on a parent is visible on a subclass via _get_marker."""

        @command
        class BaseCmd:
            pass

        class SubCmd(BaseCmd):
            pass

        assert _get_marker(SubCmd, "__cqrs_type__") == "command"

    def test_ddd_marker_visible_on_subclass(self) -> None:
        """A DDD marker set on a parent is visible on a subclass via _get_marker."""

        @aggregate
        class BaseAgg:
            pass

        class SubAgg(BaseAgg):
            pass

        assert _get_marker(SubAgg, "__ddd_type__") == "aggregate"
