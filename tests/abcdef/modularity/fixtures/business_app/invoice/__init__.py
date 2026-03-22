"""Invoice management — generates invoices when orders are confirmed, tracks invoice state and payment status.

Generate invoices from confirmed orders, track invoice state (draft → issued → paid → voided),
apply taxes and calculate totals, support invoice modifications and voiding, maintain billing history.
"""

from abcdef.c import Command, Document, Query
from abcdef.d import DomainEvent


@Command
class CreateInvoice:
    """Generate invoice for a confirmed order."""
    pass


@Command
class VoidInvoice:
    """Void an unpaid invoice."""
    pass


@Query
class GetInvoice:
    """Retrieve invoice details by invoice number."""
    pass


@Query
class GetCustomerBillingHistory:
    """Get all invoices and payments for a customer."""
    pass


@Query
class SearchInvoices:
    """Search invoices by status, date, customer, amount."""
    pass


@Document
class Invoice:
    """Complete invoice with line items, taxes, totals, and payment status."""
    pass


class InvoiceRepository:
    """Abstract repository for invoice persistence."""
    pass


class TaxCalculator:
    """Calculate taxes based on jurisdiction and product type."""
    pass


class InvoiceCreated(DomainEvent):
    """Invoice generated for confirmed order."""
    event_type = "invoice.created"


class InvoicePaid(DomainEvent):
    """Invoice fully paid."""
    event_type = "invoice.paid"


class InvoicePartiallyPaid(DomainEvent):
    """Partial payment received."""
    event_type = "invoice.partially_paid"


class InvoiceVoided(DomainEvent):
    """Invoice cancelled without payment."""
    event_type = "invoice.voided"


__modularity__ = {
    "type": "command",
}

__all__ = [
    "CreateInvoice",
    "GetCustomerBillingHistory",
    "GetInvoice",
    "Invoice",
    "InvoiceCreated",
    "InvoicePaid",
    "InvoicePartiallyPaid",
    "InvoiceRepository",
    "InvoiceVoided",
    "SearchInvoices",
    "TaxCalculator",
    "VoidInvoice",
]
