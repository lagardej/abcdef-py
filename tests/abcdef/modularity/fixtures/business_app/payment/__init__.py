"""Payment processing — processes customer payments, tracks payment status, handles failures and credits.

Process customer payments (credit cards, bank transfers, etc.), track payment status and handle payment failures,
apply customer credits to invoices, maintain payment records and statements.
"""

from abcdef.c import Command, Document, Query
from abcdef.d import DomainEvent


@Command
class RecordPayment:
    """Record a payment against an invoice."""
    pass


@Command
class ApplyCredit:
    """Apply customer credit to outstanding invoices."""
    pass


@Query
class GetOutstandingBalance:
    """Calculate total amount owed by customer."""
    pass


@Document
class Payment:
    """Payment record with method, amount, timestamp."""
    pass


class PaymentProcessor:
    """External payment gateway (Stripe, PayPal, etc.)."""
    pass


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
