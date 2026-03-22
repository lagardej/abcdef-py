"""Inventory management — tracks stock levels, manages reservations.

Handles stock replenishment.

- Maintain accurate stock counts for all products
- Reserve stock when orders are placed
- Release reservations when orders are cancelled
- Detect stock shortages and trigger replenishment
- Provide inventory availability for order validation
"""

from __future__ import annotations

from dataclasses import dataclass

from abcdef.c import Command, Document, Query
from abcdef.d import DomainEvent


# Commands
@dataclass
class AdjustStockLevel(Command):
    """Manually adjust inventory (replenishment, shrinkage, etc.)."""

    pass


@dataclass
class ReleaseReservation(Command):
    """Release a previously made reservation."""

    pass


@dataclass
class ReserveStock(Command):
    """Reserve quantity of items for an order."""

    pass


# Queries
@dataclass
class CheckAvailability(Query):
    """Check if sufficient stock exists for order fulfillment."""

    pass


@dataclass
class GetReservations(Query):
    """Find all active reservations for a product or order."""

    pass


@dataclass
class GetStockLevel(Query):
    """Get current available quantity for a product."""

    pass


# Documents
@dataclass
class InventoryLevel(Document):
    """Current stock count and reserved quantities per product."""

    pass


@dataclass
class StockReservation(Document):
    """Details of a reservation (order, quantity, expiry)."""

    pass


# SPIs
class InventoryRepository:
    """Abstract repository for inventory and reservations."""

    pass


class WarehouseManagementSystem:
    """Integration with external WMS for complex operations."""

    pass


# Events
class LowStockWarning(DomainEvent):
    """Stock fell below threshold."""

    event_type = "inventory.low_stock_warning"


class ReservationReleased(DomainEvent):
    """Reservation cancelled (order cancelled or modified)."""

    event_type = "inventory.reservation_released"


class StockAdjusted(DomainEvent):
    """Inventory levels changed (replenishment, loss, etc.)."""

    event_type = "inventory.stock_adjusted"


class StockDepleted(DomainEvent):
    """Product completely out of stock."""

    event_type = "inventory.stock_depleted"


class StockReserved(DomainEvent):
    """Stock successfully reserved for an order."""

    event_type = "inventory.stock_reserved"


__modularity__ = {
    "type": "command",
}

__all__ = [
    "AdjustStockLevel",
    "CheckAvailability",
    "GetReservations",
    "GetStockLevel",
    "InventoryLevel",
    "InventoryRepository",
    "LowStockWarning",
    "ReleaseReservation",
    "ReservationReleased",
    "ReserveStock",
    "StockAdjusted",
    "StockDepleted",
    "StockReservation",
    "StockReserved",
    "WarehouseManagementSystem",
]
