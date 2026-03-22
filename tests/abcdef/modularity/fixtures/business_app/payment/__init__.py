"""Payment processing — processes customer payments, tracks status.

Handles failures and credits.

- Process customer payments (credit cards, bank transfers, etc.)
- Track payment status and handle payment failures
- Apply customer credits to invoices
- Maintain payment records and statements
"""

from __future__ import annotations

from dataclasses import dataclass

from abcdef.c import Command, Document, Query
from abcdef.d import DomainEvent


# Commands
@dataclass
class RecordPayment(Command):
    """Record a payment against an invoice."""

    pass


@dataclass
class ApplyCredit(Command):
    """Apply customer credit to outstanding invoices."""

    pass


# Queries
@dataclass
class GetOutstandingBalance(Query):
    """Calculate total amount owed by customer."""

    pass


# Documents
@dataclass
class Payment(Document):
    """Payment record with method, amount, timestamp."""

    pass


# SPIs
class PaymentProcessor:
    """External payment gateway (Stripe, PayPal, etc.)."""

    pass


# Events
class CreditApplied(DomainEvent):
    """Customer credit used to offset invoice."""

    event_type = "payment.credit_applied"


class PaymentFailed(DomainEvent):
    """Payment attempt failed (card declined, etc.)."""

    event_type = "payment.failed"


class PaymentRecorded(DomainEvent):
    """Payment successfully processed."""

    event_type = "payment.recorded"


class PaymentReceived(DomainEvent):
    """Payment notification (alias for external event)."""

    event_type = "payment.received"


__modularity__ = {
    "type": "command",
}

__all__ = [
    "ApplyCredit",
    "CreditApplied",
    "GetOutstandingBalance",
    "Payment",
    "PaymentFailed",
    "PaymentProcessor",
    "PaymentReceived",
    "PaymentRecorded",
    "RecordPayment",
]
