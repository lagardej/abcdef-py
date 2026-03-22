"""Reporting — Analytics and read-optimized queries providing business intelligence, dashboards, and ad-hoc querying without impacting operational modules.

Serve as query-only module (CQRS), provide pre-computed aggregates for performance,
generate business reports and dashboards, track KPI metrics (conversion rate, average order value, etc.),
maintain materialized views for common queries.
"""

from abcdef.c import Document, Query


@Query
class GetCustomerLifetimeValue:
    """Total spend and retention metrics per customer."""
    pass


@Query
class GetInventoryTurnover:
    """How quickly inventory sells (by product)."""
    pass


@Query
class GetModuleHealth:
    """Operational metrics per module (event processing lag, error rates)."""
    pass


@Query
class GetPaymentSuccessRate:
    """Percentage of successful vs failed payments."""
    pass


@Query
class GetSalesReport:
    """Revenue, orders, average order value by period."""
    pass


@Query
class GetShippingPerformance:
    """On-time delivery rates by carrier and region."""
    pass


@Document
class CustomerAnalytics:
    """Customer behavior and value metrics."""
    pass


@Document
class OperationalDashboard:
    """System health and business health indicators."""
    pass


@Document
class SalesMetrics:
    """Aggregated sales data for dashboard visualization."""
    pass


class MetricsCollector:
    """Collects operational metrics from modules."""
    pass


class ReportRepository:
    """Read-optimized database/repository for reporting data."""
    pass


__modularity__ = {
    "type": "query",
}

__all__ = [
    "CustomerAnalytics",
    "GetCustomerLifetimeValue",
    "GetInventoryTurnover",
    "GetModuleHealth",
    "GetPaymentSuccessRate",
    "GetSalesReport",
    "GetShippingPerformance",
    "MetricsCollector",
    "OperationalDashboard",
    "ReportRepository",
    "SalesMetrics",
]
