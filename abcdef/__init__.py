"""ABCDEF — A Basic CQRS, DDD, Event-Sourcing Framework.

Root package. This package exports nothing directly; import from sub-packages:

    abcdef.core        -- shared primitives: Event, Message, Result, markers
    abcdef.c           -- CQRS building blocks
    abcdef.d           -- DDD building blocks
    abcdef.de          -- DDD + Event Sourcing intersection
    abcdef.in_memory   -- in-memory implementations for testing
    abcdef.specification -- Specification pattern
"""

__all__: list[str] = []
