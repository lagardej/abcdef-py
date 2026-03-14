"""Document abstraction for query-side read models."""

from . import markers


@markers.document
class Document:
    """Marker base class for query-side read models (documents).

    A Document is a denormalised, query-optimised data container built from
    domain events. It carries no behaviour and enforces no invariants —
    those concerns belong to the write side.

    Documents are persisted in and retrieved from a DocumentStore.
    Each concrete document type defines its own fields, shaped for a
    specific query pattern.
    """

    pass
