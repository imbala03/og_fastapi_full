# Widget-to-API Mapping

Exact mapping from UI widgets/screens to API calls and their request/response field names.

---

## 1. Auth

### 1.1 Login screen (email/phone + password)

| Item | Value |
|------|--------|
| **Widget / Screen** | Login form (identifier input, password input, submit button) |
| **API** | `POST /auth/login` |
| **Request (body)** | |
| → `identifier` | string — email or phone |
| → `password` | string — plain text |
| **Response (body)** | |
| ← `id` | int |
| ← `name` | string |
| ← `email` | string \| null |
| ← `phone` | string \| null |
| ← `role` | string (super_admin, admin, agent, customer, poweradmin) |
| ← `status` | string |
| ← `last_login` | datetime \| null |
| ← `created_at` | datetime |
| ← `updated_at` | datetime |

---

## 2. Users

### 2.1 User list (all users)

| Item | Value |
|------|--------|
| **Widget / Screen** | Users list / admin user table |
| **API** | `GET /users/` |
| **Request** | (none) |
| **Response (body)** | Array of: |
| ← `id` | int |
| ← `name` | string |
| ← `email` | string \| null |
| ← `phone` | string \| null |
| ← `role` | string |
| ← `status` | string |
| ← `last_login` | datetime \| null |
| ← `created_at` | datetime |
| ← `updated_at` | datetime |

### 2.2 User list (exclude poweradmin)

| Item | Value |
|------|--------|
| **Widget / Screen** | User list filtered (no poweradmin) |
| **API** | `GET /users/exclude-poweradmin` |
| **Request** | (none) |
| **Response (body)** | Same as 2.1 (array of user objects) |

### 2.3 User list by role

| Item | Value |
|------|--------|
| **Widget / Screen** | User list filtered by role (e.g. agents only) |
| **API** | `GET /users/role/{role}` |
| **Request (path)** | |
| → `role` | string — super_admin, admin, agent, customer, poweradmin |
| **Response (body)** | Same as 2.1 (array of user objects) |

### 2.4 Get user password hash

| Item | Value |
|------|--------|
| **Widget / Screen** | Admin tool / user password info |
| **API** | `GET /users/password-hash` |
| **Request (query)** | One of: |
| → `user_id` | int (optional) |
| → `username` | string (optional) — matches name |
| → `email` | string (optional) |
| **Response (body)** | |
| ← `id` | int |
| ← `name` | string |
| ← `email` | string \| null |
| ← `phone` | string \| null |
| ← `password_hash` | string |
| ← `note` | string |

### 2.5 Create user

| Item | Value |
|------|--------|
| **Widget / Screen** | Add user form |
| **API** | `POST /users/` |
| **Request (body)** | |
| → `name` | string (required) |
| → `email` | string \| null |
| → `phone` | string \| null |
| → `password` | string (required, min 6) — stored as bcrypt hash |
| → `role` | string (optional, default customer) |
| **Response (body)** | Same as 2.1 (single user object, no password) |

---

## 3. Customers

### 3.1 Customer list

| Item | Value |
|------|--------|
| **Widget / Screen** | Customer list / table |
| **API** | `GET /customers/` |
| **Request** | (none) |
| **Response (body)** | Array of: |
| ← `id` | int |
| ← `shop_name` | string |
| ← `owner_name` | string |
| ← `phone` | string |
| ← `phone2` | string \| null |
| ← `address` | string |
| ← `pincode` | string \| null |
| ← `latitude` | float \| null |
| ← `longitude` | float \| null |
| ← `created_at` | datetime |

### 3.2 Customer detail

| Item | Value |
|------|--------|
| **Widget / Screen** | Customer detail / profile view |
| **API** | `GET /customers/{customer_id}` |
| **Request (path)** | |
| → `customer_id` | int |
| **Response (body)** | Same fields as 3.1 (single object) |

### 3.3 Create customer

| Item | Value |
|------|--------|
| **Widget / Screen** | Add customer form |
| **API** | `POST /customers/` |
| **Request (body)** | |
| → `shop_name` | string |
| → `owner_name` | string |
| → `phone` | string |
| → `phone2` | string \| null |
| → `address` | string |
| → `pincode` | string \| null |
| → `latitude` | float \| null |
| → `longitude` | float \| null |
| **Response (body)** | Same as 3.1 (single object with `id`, `created_at`) |

### 3.4 Delete customer

| Item | Value |
|------|--------|
| **Widget / Screen** | Customer row action / delete confirmation |
| **API** | `DELETE /customers/{customer_id}` |
| **Request (path)** | |
| → `customer_id` | int |
| **Response (body)** | `{ "message": "Customer deleted successfully" }` |

---

## 4. Orders

### 4.1 Order list (all)

| Item | Value |
|------|--------|
| **Widget / Screen** | Orders list / table |
| **API** | `GET /orders/` |
| **Request** | (none) |
| **Response (body)** | Array of: |
| ← `order_id` | int |
| ← `customer_id` | int \| null |
| ← `trays_taken` | int |
| ← `trays_returned` | int |
| ← `trays_holding` | int |
| ← `bottles_holding` | int |
| ← `bottles_returned` | int |
| ← `bottles_damaged` | int |
| ← `payment_status` | string \| null |
| ← `delivered_by` | int \| null |
| ← `review_status` | string \| null |
| ← `created_at` | datetime |

### 4.2 Order detail

| Item | Value |
|------|--------|
| **Widget / Screen** | Order detail / edit screen |
| **API** | `GET /orders/{order_id}` |
| **Request (path)** | |
| → `order_id` | int |
| **Response (body)** | Same as 4.1 (single object) |

### 4.3 Orders by customer

| Item | Value |
|------|--------|
| **Widget / Screen** | Customer’s order history list |
| **API** | `GET /orders/customer/{id}` |
| **Request (path)** | |
| → `id` | int — customer_id |
| **Response (body)** | Same as 4.1 (array) |

### 4.4 Customer latest holdings (trays/bottles)

| Item | Value |
|------|--------|
| **Widget / Screen** | Customer summary card / holdings widget |
| **API** | `GET /orders/customer/{customer_id}/latest-holdings` |
| **Request (path)** | |
| → `customer_id` | int |
| **Response (body)** | |
| ← `order_id` | int |
| ← `created_at` | datetime |
| ← `trays_holding` | int |
| ← `bottles_holding` | int |
| ← `bottles_damaged` | int |

### 4.5 Orders by deliverer

| Item | Value |
|------|--------|
| **Widget / Screen** | Agent’s delivery list |
| **API** | `GET /orders/delivered-by/{delivered_by}` |
| **Request (path)** | |
| → `delivered_by` | int — user id |
| **Response (body)** | Same as 4.1 (array) |

### 4.6 Agent order summary

| Item | Value |
|------|--------|
| **Widget / Screen** | Agent dashboard / stats card |
| **API** | `GET /orders/agent/{user_id}/summary` |
| **Request (path)** | |
| → `user_id` | int |
| **Response (body)** | |
| ← `total_orders` | int |
| ← `total_trays_outside` | int |
| ← `total_trays_received` | int |
| ← `total_bottles_delivered` | int |
| ← `total_bottles_returned` | int |
| ← `total_bottles_damaged` | int |

### 4.7 Order summary by date

| Item | Value |
|------|--------|
| **Widget / Screen** | Date filter / daily summary widget |
| **API** | `GET /orders/summary/by-date?timestamp=...` |
| **Request (query)** | |
| → `timestamp` | datetime — e.g. 2026-03-07 or 2026-03-07T00:00:00 |
| **Response (body)** | |
| ← `total_orders` | int |
| ← `total_trays_outside` | int |
| ← `trays_received_back` | int |
| ← `total_bottles_outside` | int |
| ← `bottles_returned` | int |
| ← `bottles_damaged` | int |

### 4.8 Create order

| Item | Value |
|------|--------|
| **Widget / Screen** | New order form |
| **API** | `POST /orders/` |
| **Request (body)** | |
| → `customer_id` | int \| null |
| → `trays_taken` | int (default 0) |
| → `trays_returned` | int (default 0) |
| → `bottles_holding` | int (default 0) |
| → `bottles_returned` | int (default 0) |
| → `bottles_damaged` | int (default 0) |
| → `payment_status` | string \| null |
| → `delivered_by` | int \| null |
| → `review_status` | string \| null |
| **Response (body)** | Same as 4.1 (single object; `trays_holding` computed by API) |

### 4.9 Update order

| Item | Value |
|------|--------|
| **Widget / Screen** | Order edit form |
| **API** | `PUT /orders/{order_id}` |
| **Request (path)** | |
| → `order_id` | int |
| **Request (body)** | Any subset of: |
| → `customer_id` | int \| null |
| → `trays_taken` | int |
| → `trays_returned` | int |
| → `bottles_holding` | int |
| → `bottles_returned` | int |
| → `bottles_damaged` | int |
| → `payment_status` | string \| null |
| → `delivered_by` | int \| null |
| → `review_status` | string \| null |
| **Response (body)** | Same as 4.1 (single object) |

### 4.10 Delete order

| Item | Value |
|------|--------|
| **Widget / Screen** | Order row action / delete |
| **API** | `DELETE /orders/{order_id}` |
| **Request (path)** | |
| → `order_id` | int |
| **Response (body)** | `{ "message": "Order deleted successfully" }` |

---

## 5. Order temp (draft / temporary orders)

### 5.1 Temp order list

| Item | Value |
|------|--------|
| **Widget / Screen** | Draft orders list |
| **API** | `GET /order-temp/` |
| **Request** | (none) |
| **Response (body)** | Array of: |
| ← `order_id` | int |
| ← `customer_id` | int \| null |
| ← `trays_taken` | int |
| ← `trays_returned` | int |
| ← `trays_holding` | int |
| ← `bottles_holding` | int |
| ← `bottles_returned` | int |
| ← `bottles_damaged` | int |
| ← `payment_status` | string \| null |
| ← `delivered_by` | int \| null |
| ← `review_status` | string \| null |
| ← `created_at` | datetime |

### 5.2 Temp order detail

| Item | Value |
|------|--------|
| **Widget / Screen** | Draft order detail |
| **API** | `GET /order-temp/{order_id}` |
| **Request (path)** | |
| → `order_id` | int |
| **Response (body)** | Same as 5.1 (single object) |

### 5.3 Temp orders by customer

| Item | Value |
|------|--------|
| **Widget / Screen** | Customer’s draft orders |
| **API** | `GET /order-temp/customer/{id}` |
| **Request (path)** | |
| → `id` | int — customer_id |
| **Response (body)** | Same as 5.1 (array) |

### 5.4 Temp orders by deliverer

| Item | Value |
|------|--------|
| **Widget / Screen** | Agent’s draft list |
| **API** | `GET /order-temp/delivered-by/{delivered_by}` |
| **Request (path)** | |
| → `delivered_by` | int |
| **Response (body)** | Same as 5.1 (array) |

### 5.5 Create temp order

| Item | Value |
|------|--------|
| **Widget / Screen** | New draft order form |
| **API** | `POST /order-temp/` |
| **Request (body)** | |
| → `customer_id` | int \| null |
| → `trays_taken` | int (default 0) |
| → `trays_returned` | int (default 0) |
| → `bottles_holding` | int (default 0) |
| → `bottles_returned` | int (default 0) |
| → `bottles_damaged` | int (default 0) |
| → `payment_status` | string \| null |
| → `delivered_by` | int \| null |
| → `review_status` | string \| null |
| **Response (body)** | Same as 5.1 (single object) |

### 5.6 Update temp order

| Item | Value |
|------|--------|
| **Widget / Screen** | Edit draft order form |
| **API** | `PUT /order-temp/{order_id}` |
| **Request (path)** | |
| → `order_id` | int |
| **Request (body)** | Any subset of same fields as 5.5 |
| **Response (body)** | Same as 5.1 (single object) |

### 5.7 Delete temp order

| Item | Value |
|------|--------|
| **Widget / Screen** | Draft row delete action |
| **API** | `DELETE /order-temp/{order_id}` |
| **Request (path)** | |
| → `order_id` | int |
| **Response (body)** | `{ "message": "Order deleted successfully" }` (or similar) |

---

## 6. Admin

### 6.1 Admin dashboard metrics

| Item | Value |
|------|--------|
| **Widget / Screen** | Admin dashboard (totals, payment breakdown) |
| **API** | `GET /admin/metrics` |
| **Request** | (none) |
| **Response (body)** | |
| ← `total_customers` | int |
| ← `total_orders` | int |
| ← `payment_status_summary` | object — e.g. `{ "paid": 10, "pending": 2 }` |

---

## 7. Health (optional widget)

### 7.1 Health check

| Item | Value |
|------|--------|
| **Widget / Screen** | Status indicator / monitoring |
| **API** | `GET /health` |
| **Request** | (none) |
| **Response (body)** | |
| ← `status` | string — "healthy" or "unhealthy" |
| ← `database` | string — "connected" or "disconnected" |

---

## Quick reference: widget → API

| Widget / Screen | Method | Path |
|-----------------|--------|------|
| Login form | POST | /auth/login |
| User list | GET | /users/ |
| User list (no poweradmin) | GET | /users/exclude-poweradmin |
| User list by role | GET | /users/role/{role} |
| User password hash | GET | /users/password-hash?user_id=... |
| Create user | POST | /users/ |
| Customer list | GET | /customers/ |
| Customer detail | GET | /customers/{customer_id} |
| Create customer | POST | /customers/ |
| Delete customer | DELETE | /customers/{customer_id} |
| Order list | GET | /orders/ |
| Order detail | GET | /orders/{order_id} |
| Orders by customer | GET | /orders/customer/{id} |
| Customer latest holdings | GET | /orders/customer/{customer_id}/latest-holdings |
| Orders by deliverer | GET | /orders/delivered-by/{delivered_by} |
| Agent summary | GET | /orders/agent/{user_id}/summary |
| Order summary by date | GET | /orders/summary/by-date?timestamp=... |
| Create order | POST | /orders/ |
| Update order | PUT | /orders/{order_id} |
| Delete order | DELETE | /orders/{order_id} |
| Temp order list | GET | /order-temp/ |
| Temp order detail | GET | /order-temp/{order_id} |
| Temp orders by customer | GET | /order-temp/customer/{id} |
| Temp orders by deliverer | GET | /order-temp/delivered-by/{delivered_by} |
| Create temp order | POST | /order-temp/ |
| Update temp order | PUT | /order-temp/{order_id} |
| Delete temp order | DELETE | /order-temp/{order_id} |
| Admin metrics | GET | /admin/metrics |
| Health check | GET | /health |
