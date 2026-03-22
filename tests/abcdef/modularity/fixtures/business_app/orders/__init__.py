"""Order management — creates, tracks, and fulfills customer orders throughout their lifecycle.

Accept new orders from customers, validate orders (credit, inventory availability via events),
manage order state (draft → placed → confirmed → fulfilled → cancelled),
coordinate order lifecycle across modules through events, support order modifications and cancellations.
"""

from abcdef.c import Command, Document, Query
from abcdef.d import DomainEvent


@Command
class CancelOrder:
    """Cancel an order (if not yet fulfilled)."""
    pass


@Command
class ConfirmOrder:
    """Mark order as confirmed after validations pass."""
    pass


@Command
class CreateOrder:
    """Create a new draft order for a customer."""
    pass


@Command
class PlaceOrder:
    """Submit an order for processing."""
    pass


@Command
class UpdateOrderLine:
    """Modify items in a draft order."""
    pass


@Query
class GetCustomerOrders:
    """Find all orders for a specific customer."""
    pass


@Query
class GetOrderDetails:
    """Retrieve full order information including all lines and status."""
    pass


@Query
class SearchOrders:
    """Search orders by ID, status, date range, customer."""
    pass


@Document
class Order:
    """Complete order read model with lines, status, and history."""
    pass


@Document
class OrderSummary:
    """Summary view for order listings."""
    pass


class OrderNumberGenerator:
    """Generates unique order identifiers."""
    pass


class OrderRepository:
    """Abstract repository for order persistence."""
    pass


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
