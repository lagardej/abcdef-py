"""Inventory management — tracks stock levels, manages reservations, and handles stock replenishment.

Maintain accurate stock counts for all products, reserve stock when orders are placed,
release reservations when orders are cancelled, detect stock shortages and trigger replenishment,
provide inventory availability for order validation.
"""

from abcdef.c import Command, Document, Query
from abcdef.d import DomainEvent


@Command
class AdjustStockLevel:
    """Manually adjust inventory (replenishment, shrinkage, etc.)."""
    pass


@Command
class ReleaseReservation:
    """Release a previously made reservation."""
    pass


@Command
class ReserveStock:
    """Reserve quantity of items for an order."""
    pass


@Query
class CheckAvailability:
    """Check if sufficient stock exists for order fulfillment."""
    pass


@Query
class GetReservations:
    """Find all active reservations for a product or order."""
    pass


@Query
class GetStockLevel:
    """Get current available quantity for a product."""
    pass


@Document
class InventoryLevel:
    """Current stock count and reserved quantities per product."""
    pass


@Document
class StockReservation:
    """Details of a reservation (order, quantity, expiry)."""
    pass


class InventoryRepository:
    """Abstract repository for inventory and reservations."""
    pass


class WarehouseManagementSystem:
    """Integration with external WMS for complex operations."""
    pass


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
