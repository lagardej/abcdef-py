"""ABCDEF package map.

This root package exports nothing directly. Import from the public subpackages:

    abcdef.b             -- shared foundational primitives
    abcdef.c             -- CQRS building blocks
    abcdef.d             -- DDD building blocks
    abcdef.de            -- event-sourced DDD extensions
    abcdef.in_memory     -- in-memory adapters for tests and local runs
    abcdef.specification -- specification pattern support
    abcdef.modulith      -- modular architecture validation and documentation
"""

__all__: list[str] = []
