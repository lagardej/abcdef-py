"""Modularity architecture markers.

Markers that declare architectural concepts specific to modularity:
module type declaration and Service Provider Interface (SPI) exposure.

Marker attribute convention:
- modularity/ uses ``__modularity_type__``
"""

# Constants for module type declaration
COMMAND_MODULE = "command"
QUERY_MODULE = "query"
SPI = "spi"

__all__ = [
    "COMMAND_MODULE",
    "QUERY_MODULE",
    "SPI",
]
