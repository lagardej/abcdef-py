# Business Application - Module Documentation

This document describes the public API and inter-module communication for all modules in Business application. Implementation details are omitted.

## Table of Contents

- [Modules](#modules)
- [Cross-Module Reference](#cross-module-reference)

## Modules

- **[Invoice](#invoice)** — [API](#invoice-public-api) · [Events](#invoice-events)
- **[Inventory](#inventory)** — [API](#inventory-public-api) · [Events](#inventory-events)
- **[Orders](#orders)** — [API](#orders-public-api) · [Events](#orders-events)
- **[Payment](#payment)** — [API](#payment-public-api) · [Events](#payment-events)
- **[Reporting](#reporting)** — [API](#reporting-public-api) · [Events](#reporting-events)

______________________________________________________________________

## Invoice

Invoice management — generates invoices when orders are confirmed, tracks invoice state and payment status.

- Generate invoices from confirmed orders
- Track invoice state (draft → issued → paid → voided)
- Apply taxes and calculate totals
- Support invoice modifications and voiding
- Maintain billing history

### Invoice Public API

| Command | |
| - | - |
| `CreateInvoice` | Generate invoice for a confirmed order. |
| `VoidInvoice` | Void an unpaid invoice. |

| Query | |
| - | - |
| `GetInvoice` | Retrieve invoice details by invoice number. |
| `GetCustomerBillingHistory` | Get all invoices and payments for a customer. |
| `SearchInvoices` | Search invoices by status, date, customer, amount. |

| Document | |
| - | - |
| `Invoice` | Complete invoice with line items, taxes, totals, and payment status. |

| SPI | |
| - | - |
| `InvoiceRepository` | Abstract repository for invoice persistence. |
| `TaxCalculator` | Calculate taxes based on jurisdiction and product type. |

### Invoice Events

**Events Published:**

- `InvoiceCreated` — Invoice generated for confirmed order
- `InvoicePaid` — Invoice fully paid
- `InvoicePartiallyPaid` — Partial payment received
- `InvoiceVoided` — Invoice cancelled without payment

**Events Subscribed:**

- `OrderConfirmed` — Trigger invoice creation

______________________________________________________________________

## Inventory

Inventory management — tracks stock levels, manages reservations, and handles stock replenishment.

- Maintain accurate stock counts for all products
- Reserve stock when orders are placed
- Release reservations when orders are cancelled
- Detect stock shortages and trigger replenishment
- Provide inventory availability for order validation

### Inventory Public API

| Command | |
| - | - |
| `AdjustStockLevel` | Manually adjust inventory (replenishment, shrinkage, etc.). |
| `ReleaseReservation` | Release a previously made reservation. |
| `ReserveStock` | Reserve quantity of items for an order. |

| Query | |
| - | - |
| `CheckAvailability` | Check if sufficient stock exists for order fulfillment. |
| `GetReservations` | Find all active reservations for a product or order. |
| `GetStockLevel` | Get current available quantity for a product. |

| Document | |
| - | - |
| `InventoryLevel` | Current stock count and reserved quantities per product. |
| `StockReservation` | Details of a reservation (order, quantity, expiry). |

| SPI | |
| - | - |
| `InventoryRepository` | Abstract repository for inventory and reservations. |
| `WarehouseManagementSystem` | Integration with external WMS for complex operations. |

### Inventory Events

**Events Published:**

- `LowStockWarning` — Stock fell below threshold
- `ReservationReleased` — Reservation cancelled (order cancelled or modified)
- `StockAdjusted` — Inventory levels changed (replenishment, loss, etc.)
- `StockDepleted` — Product completely out of stock
- `StockReserved` — Stock successfully reserved for an order

**Events Subscribed:**

- `OrderCancelled` — Release reservation for cancelled order
- `OrderLineUpdated` — Adjust reservations based on quantity changes
- `OrderPlaced` — Reserve stock for new order (async)

______________________________________________________________________

## Orders

Order management — creates, tracks, and fulfills customer orders throughout their lifecycle.

- Accept new orders from customers
- Validate orders (credit, inventory availability via events)
- Manage order state (draft → placed → confirmed → fulfilled → cancelled)
- Coordinate order lifecycle across modules through events
- Support order modifications and cancellations

### Orders Public API

| Command | |
| - | - |
| `CancelOrder` | Cancel an order (if not yet fulfilled). |
| `ConfirmOrder` | Mark order as confirmed after validations pass. |
| `CreateOrder` | Create a new draft order for a customer. |
| `PlaceOrder` | Submit an order for processing. |
| `UpdateOrderLine` | Modify items in a draft order. |

| Query | |
| - | - |
| `GetCustomerOrders` | Find all orders for a specific customer. |
| `GetOrderDetails` | Retrieve full order information including all lines and status. |
| `SearchOrders` | Search orders by ID, status, date range, customer. |

| Document | |
| - | - |
| `Order` | Complete order read model with lines, status, and history. |
| `OrderSummary` | Summary view for order listings. |

| SPI | |
| - | - |
| `OrderNumberGenerator` | Generates unique order identifiers. |
| `OrderRepository` | Abstract repository for order persistence. |

### Orders Events

**Events Published:**

- `OrderCancelled` — Order cancelled by customer or system
- `OrderConfirmed` — Order passed all validations, ready for fulfillment
- `OrderCreated` — New draft order created (before validation)
- `OrderLineUpdated` — Order line item changed
- `OrderPlaced` — Order submitted for processing

**Events Subscribed:**

- `InvoiceCreated` — Billing generated for this order
- `InventoryReserved` — Stock allocated, confirms order can be fulfilled
- `StockRejected` — Inventory unavailable, order cannot proceed (triggers cancellation or hold)

______________________________________________________________________

## Payment

Payment processing — processes customer payments, tracks payment status, handles failures and credits.

- Process customer payments (credit cards, bank transfers, etc.)
- Track payment status and handle payment failures
- Apply customer credits to invoices
- Maintain payment records and statements

### Payment Public API

| Command | |
| - | - |
| `RecordPayment` | Record a payment against an invoice. |
| `ApplyCredit` | Apply customer credit to outstanding invoices. |

| Query | |
| - | - |
| `GetOutstandingBalance` | Calculate total amount owed by customer. |

| Document | |
| - | - |
| `Payment` | Payment record with method, amount, timestamp. |

| SPI | |
| - | - |
| `PaymentProcessor` | External payment gateway (Stripe, PayPal, etc.). |

### Payment Events

**Events Published:**

- `CreditApplied` — Customer credit used to offset invoice
- `PaymentFailed` — Payment attempt failed (card declined, etc.)
- `PaymentRecorded` — Payment successfully processed
- `PaymentReceived` — Payment notification (alias for external event)

______________________________________________________________________

## Reporting

Analytics and read-optimized queries — provides business intelligence, dashboards, and ad-hoc querying without impacting operational modules.

- Serve as query-only module (CQRS)
- Provide pre-computed aggregates for performance
- Generate business reports and dashboards
- Track KPI metrics (conversion rate, average order value, etc.)
- Maintain materialized views for common queries

### Reporting Public API

| Query | |
| - | - |
| `GetCustomerLifetimeValue` | Total spend and retention metrics per customer. |
| `GetInventoryTurnover` | How quickly inventory sells (by product). |
| `GetModuleHealth` | Operational metrics per module (event processing lag, error rates). |
| `GetPaymentSuccessRate` | Percentage of successful vs failed payments. |
| `GetSalesReport` | Revenue, orders, average order value by period. |
| `GetShippingPerformance` | On-time delivery rates by carrier and region. |

| Document | |
| - | - |
| `CustomerAnalytics` | Customer behavior and value metrics. |
| `OperationalDashboard` | System health and business health indicators. |
| `SalesMetrics` | Aggregated sales data for dashboard visualization. |

| SPI | |
| - | - |
| `MetricsCollector` | Collects operational metrics from modules. |
| `ReportRepository` | Read-optimized database/repository for reporting data. |

### Reporting Events

**Events Subscribed:**

- `InvoiceCreated` — Invoice generated for confirmed order
- `PaymentRecorded` — Payment successfully processed
- `OrderCreated` — New draft order created (before validation)
- `OrderConfirmed` — Order passed all validations, ready for fulfillment
- `OrderCancelled` — Order cancelled by customer or system
- `StockAdjusted` — Inventory levels changed (replenishment, loss, etc.)
- `LowStockWarning` — Stock fell below threshold

---

## Cross-Module Reference

### Event Cross-Reference

| Category | Event | Published by | Subscribed by |
| - | - | - | - |
| Billing | CreditApplied | Payment |  |
| Billing | InvoiceCreated | Invoice | Orders, Reporting |
| Billing | InvoicePaid | Invoice |  |
| Billing | InvoicePartiallyPaid | Invoice |  |
| Billing | InvoiceVoided | Invoice |  |
| Billing | PaymentFailed | Payment |  |
| Billing | PaymentRecorded | Payment | Reporting |
| Billing | PaymentReceived | Payment |  |
| Inventory | LowStockWarning | Inventory | Reporting |
| Inventory | ReservationReleased | Inventory |  |
| Inventory | StockAdjusted | Inventory | Reporting |
| Inventory | StockDepleted | Inventory |  |
| Inventory | StockReserved | Inventory |  |
| Order | OrderCancelled | Orders | Inventory, Reporting |
| Order | OrderConfirmed | Orders | Invoice, Reporting |
| Order | OrderCreated | Orders | Reporting |
| Order | OrderLineUpdated | Orders | Inventory |
| Order | OrderPlaced | Orders | Inventory |

---

## Module Interaction Rules

1. **No direct method calls** between modules — all communication via events or queries
2. **Commands** are synchronous; handlers complete before returning
3. **Events** are asynchronous; subscribers process independently, in parallel
4. **Idempotency** required: Event handlers must handle duplicate delivery
5. **No circular dependencies**: Module A → event → Module B → event → Module A is an anti-pattern
6. **SPI interfaces** are module-private; implementations exist within the same module only
7. **Reporting** subscribes to all events but emits none; it maintains denormalized views
