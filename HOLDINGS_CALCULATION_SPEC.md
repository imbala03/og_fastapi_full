# How trays_holding and bottles_holding are calculated

## Formulas (Model A)

Both values are **derived on the server only**. The client never sends holding; it sends taken and returned.

| Field            | Formula                          | Meaning (per order)                          |
|------------------|-----------------------------------|----------------------------------------------|
| **trays_holding**  | `trays_taken - trays_returned`   | Net trays from that order.                   |
| **bottles_holding** | `bottles_taken - bottles_returned` | Net bottles from that order.               |

When **nothing is returned** (returned = 0), holding = taken for that order. So 1 tray taken → trays_holding = 1; 2 bottles taken → bottles_holding = 2.

---

## Per-order vs customer total (avoiding discrepancy)

- **Per order:** Each row has its own `trays_holding` and `bottles_holding` (taken − returned for that order). This is correct and stored.
- **Customer total:** To get “how many trays/bottles is this customer holding in total?” you must **sum** holding across **all** orders for that customer.

**Example (your scenario):**

- Order 7: trays_taken=1, trays_returned=0 → trays_holding=1; bottles 1,0 → bottles_holding=1.
- Order 8: trays_taken=2, trays_returned=0 → trays_holding=2; bottles 2,0 → bottles_holding=2.

**Per order (correct):** Order 7 shows 1,1; Order 8 shows 2,2.  
**Customer total (correct):** 1+2 = **3 trays**, 1+2 = **3 bottles** — use the **total-holdings** endpoint for this.

| Use case | Endpoint | Returns |
|----------|----------|--------|
| Latest order only (“last delivery”) | `GET /orders/customer/{id}/latest-holdings` | That one order’s holding (e.g. 2,2). |
| **Customer balance (no discrepancy)** | `GET /orders/customer/{id}/total-holdings` | Sum of holding across all orders (e.g. 3,3). |
| All orders (raw list) | `GET /orders/customer/{id}` | Each order with its own holding; sum in the app if needed. |

---

## Where they are calculated

### 1. Orders (`/orders`)

- **Create (POST /orders/)**  
  - Request body: `trays_taken`, `trays_returned`, `bottles_taken`, `bottles_returned` (and other fields).  
  - Server sets:
    - `trays_holding = trays_taken - trays_returned`
    - `bottles_holding = bottles_taken - bottles_returned`
  - These values are stored in the `orders` table.

- **Update (PUT /orders/{order_id})**  
  - Request body can include `trays_taken`, `trays_returned`, `bottles_taken`, `bottles_returned` (all optional).  
  - Server recomputes using **current** taken/returned (from request or existing order):
    - `trays_holding = trays_taken - trays_returned`
    - `bottles_holding = bottles_taken - bottles_returned`
  - Stored values are updated.

**Code (orders):**  
`routers/orders.py` — create: lines 37–38; update: lines 229–230.

---

### 2. Order temp (`/order-temp`)

- **Create (POST /order-temp/)**  
  - Same as orders: server sets  
    - `trays_holding = trays_taken - trays_returned`  
    - `bottles_holding = bottles_taken - bottles_returned`  
  - Stored in the `order_temp` table.

- **Update (PUT /order-temp/{order_id})**  
  - Same as orders: server recomputes holding from current taken/returned and updates the row.

**Code (order_temp):**  
`routers/order_temp.py` — create: lines 33–34; update: lines 99–100.

---

## Validation (before applying the formulas)

The server enforces these rules for both **orders** and **order_temp** (create and update):

| Rule | Error if violated |
|------|--------------------|
| `trays_taken ≥ 0` | 400: "Tray counts cannot be negative" |
| `trays_returned ≥ 0` | 400: "Tray counts cannot be negative" |
| `trays_returned ≤ trays_taken` | 400: "Trays returned cannot exceed trays taken" |
| `bottles_taken ≥ 0` | 400: "Bottle counts cannot be negative" |
| `bottles_returned ≥ 0` | 400: "Bottle counts cannot be negative" |
| `bottles_returned ≤ bottles_taken` | 400: "Bottles returned cannot exceed bottles taken" |

So **holding is always non‑negative** (taken − returned, with returned ≤ taken).

---

## Summary

- **trays_holding** = `trays_taken - trays_returned` (server-only, on create/update for orders and order_temp).
- **bottles_holding** = `bottles_taken - bottles_returned` (server-only, on create/update for orders and order_temp).
- Client sends only taken and returned; server computes and stores holding and validates the rules above.
