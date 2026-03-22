"""Order management — creates, tracks, fulfills customer orders.

Throughout their lifecycle.

- Accept new orders from customers
- Validate orders (credit, inventory availability via events)
- Manage order state (draft → placed → confirmed → fulfilled → cancelled)
- Coordinate order lifecycle across modules through events
- Support order modifications and cancellations
"""

from __future__ import annotations

from dataclasses import dataclass

from abcdef.c import Command, Document, Query
from abcdef.d import DomainEvent


# Commands
@dataclass
class CancelOrder(Command):
    """Cancel an order (if not yet fulfilled)."""

    pass


@dataclass
class ConfirmOrder(Command):
    """Mark order as confirmed after validations pass."""

    pass


@dataclass
class CreateOrder(Command):
    """Create a new draft order for a customer."""

    pass


@dataclass
class PlaceOrder(Command):
    """Submit an order for processing."""

    pass


@dataclass
class UpdateOrderLine(Command):
    """Modify items in a draft order."""

    pass


# Queries
@dataclass
class GetCustomerOrders(Query):
    """Find all orders for a specific customer."""

    pass


@dataclass
class GetOrderDetails(Query):
    """Retrieve full order information including all lines and status."""

    pass


@dataclass
class SearchOrders(Query):
    """Search orders by ID, status, date range, customer."""

    pass


# Documents
@dataclass
class Order(Document):
    """Complete order read model with lines, status, and history."""

    pass


@dataclass
class OrderSummary(Document):
    """Summary view for order listings."""

    pass


# SPIs
class OrderNumberGenerator:
    """Generates unique order identifiers."""

    pass


class OrderRepository:
    """Abstract repository for order persistence."""

    pass


# Events
class OrderCancelled(DomainEvent):
    """Order cancelled by customer or system."""

    event_type = "order.cancelled"


class OrderConfirmed(DomainEvent):
    """Order passed all validations, ready for fulfillment."""

    event_type = "order.confirmed"


class OrderCreated(DomainEvent):
    """New draft order created (before validation)."""

    event_type = "order.created"


class OrderLineUpdated(DomainEvent):
    """Order line item changed."""

    event_type = "order.line_updated"


class OrderPlaced(DomainEvent):
    """Order submitted for processing."""

    event_type = "order.placed"


__modularity__ = {
    "type": "command",
}

__all__ = [
    "CancelOrder",
    "ConfirmOrder",
    "CreateOrder",
    "GetCustomerOrders",
    "GetOrderDetails",
    "Order",
    "OrderCancelled",
    "OrderConfirmed",
    "OrderCreated",
    "OrderLineUpdated",
    "OrderNumberGenerator",
    "OrderPlaced",
    "OrderRepository",
    "OrderSummary",
    "PlaceOrder",
    "SearchOrders",
    "UpdateOrderLine",
]
