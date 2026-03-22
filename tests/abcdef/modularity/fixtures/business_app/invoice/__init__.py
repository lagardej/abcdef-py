"""Invoice management — generates invoices when orders are confirmed.

Tracks invoice state and payment status.

- Generate invoices from confirmed orders
- Track invoice state (draft → issued → paid → voided)
- Apply taxes and calculate totals
- Support invoice modifications and voiding
- Maintain billing history
"""

from __future__ import annotations

from dataclasses import dataclass

from abcdef.c import Command, Document, Query
from abcdef.d import DomainEvent


# Commands
@dataclass
class CreateInvoice(Command):
    """Generate invoice for a confirmed order."""

    pass


@dataclass
class VoidInvoice(Command):
    """Void an unpaid invoice."""

    pass


# Queries
@dataclass
class GetInvoice(Query):
    """Retrieve invoice details by invoice number."""

    pass


@dataclass
class GetCustomerBillingHistory(Query):
    """Get all invoices and payments for a customer."""

    pass


@dataclass
class SearchInvoices(Query):
    """Search invoices by status, date, customer, amount."""

    pass


# Documents
@dataclass
class Invoice(Document):
    """Complete invoice with line items, taxes, totals, and payment status."""

    pass


# SPIs
class InvoiceRepository:
    """Abstract repository for invoice persistence."""

    pass


class TaxCalculator:
    """Calculate taxes based on jurisdiction and product type."""

    pass


# Events
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
