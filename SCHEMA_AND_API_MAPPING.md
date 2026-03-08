# Database Schema & API Mapping

This document describes the database tables (schema) and how API request/response fields map to stored values.

---

## 1. Database schema (tables)

### 1.1 `users`

| Column      | Type              | Nullable | Default     | Description                    |
|------------|-------------------|----------|-------------|--------------------------------|
| id         | Integer           | NO (PK)  | —           | Primary key                    |
| name       | String(255)       | NO       | —           | Display name                   |
| email      | String(255)       | YES      | —           | Unique, indexed                |
| phone      | String(50)        | YES      | —           | Unique, indexed                |
| password   | String(255)       | NO       | —           | Bcrypt hash (never plain text)  |
| role       | Enum(UserRole)    | NO       | customer    | super_admin, admin, agent, customer, poweradmin |
| status     | String(50)        | NO       | active      |                                |
| last_login | DateTime(TZ)      | YES      | —           | Set on successful login        |
| created_at | DateTime(TZ)      | NO       | now()       |                                |
| updated_at | DateTime(TZ)      | NO       | now()       | Auto-updated on change         |

---

### 1.2 `logins`

| Column      | Type         | Nullable | Default | Description |
|------------|--------------|----------|---------|-------------|
| id         | Integer      | NO (PK)  | —       | Primary key |
| name       | String       | NO       | —       |             |
| email      | String       | NO       | —       | Unique, indexed |
| password   | String       | NO       | —       |             |
| role       | String       | NO       | —       |             |
| status     | String       | YES      | active  |             |
| last_login | DateTime(TZ) | YES      | —       |             |
| created_at | DateTime(TZ) | YES      | now()   |             |
| updated_at | DateTime(TZ) | YES      | now()   |             |

---

### 1.3 `customers`

| Column     | Type         | Nullable | Default | Description        |
|------------|--------------|----------|---------|--------------------|
| id         | Integer      | NO (PK)  | —       | Primary key        |
| shop_name  | String       | NO       | —       |                    |
| owner_name | String       | NO       | —       |                    |
| phone      | String       | NO       | —       |                    |
| phone2     | String       | YES      | —       |                    |
| address    | String       | NO       | —       |                    |
| pincode    | String       | YES      | —       |                    |
| latitude   | Float        | YES      | —       |                    |
| longitude  | Float        | YES      | —       |                    |
| created_at | DateTime(TZ) | YES      | now()   |                    |

---

### 1.4 `orders`

| Column          | Type         | Nullable | Default | Description |
|-----------------|--------------|----------|---------|-------------|
| order_id        | Integer      | NO (PK)  | auto    | Primary key, autoincrement |
| customer_id     | Integer      | YES      | —       | FK → customers.id |
| trays_taken     | Integer      | NO       | 0       |             |
| trays_holding   | Integer      | NO       | 0       | Derived: trays_taken − trays_returned |
| trays_returned  | Integer      | NO       | 0       |             |
| bottles_holding | Integer      | NO       | 0       |             |
| bottles_returned| Integer      | NO       | 0       |             |
| bottles_damaged | Integer      | NO       | 0       |             |
| payment_status  | String(50)   | YES      | —       |             |
| delivered_by    | Integer      | YES      | —       | User ID (no FK in model) |
| review_status   | String(50)   | YES      | —       |             |
| created_at      | DateTime(TZ) | NO       | now()   |             |

---

### 1.5 `order_temp`

| Column          | Type         | Nullable | Default | Description |
|-----------------|--------------|----------|---------|-------------|
| order_id        | Integer      | NO (PK)  | auto    | Primary key, autoincrement |
| customer_id     | Integer      | YES      | —       | FK → customers.id |
| trays_taken     | Integer      | NO       | 0       |             |
| trays_holding   | Integer      | NO       | 0       | Derived: trays_taken − trays_returned |
| trays_returned  | Integer      | NO       | 0       |             |
| bottles_holding | Integer      | NO       | 0       |             |
| bottles_returned| Integer      | NO       | 0       |             |
| bottles_damaged | Integer      | NO       | 0       |             |
| payment_status  | String(50)   | YES      | —       |             |
| delivered_by    | Integer      | YES      | —       |             |
| review_status   | String(50)   | YES      | —       |             |
| created_at      | DateTime(TZ) | NO       | now()   |             |

---

## 2. API → Schema → Database mapping

### 2.1 Auth (login)

| Aspect   | Source | Value / Storage |
|----------|--------|------------------|
| Endpoint | —      | `POST /auth/login` |
| Request  | Body   | `LoginRequest`: `identifier` (email or phone), `password` (plain text) |
| Storage  | —      | **Not stored as-is.** `identifier` is used to find a row in `users` by `email` or `phone`; `password` is verified against `users.password` (bcrypt). On success, `users.last_login` is updated. |
| Response | Body   | `UserOut`: from `users` — `id`, `name`, `email`, `phone`, `role`, `status`, `last_login`, `created_at`, `updated_at`. **Password is never returned.** |

| API field (request) | Database / behavior |
|---------------------|---------------------|
| identifier          | Matches `users.email` (case-insensitive) or `users.phone` |
| password            | Compared with `users.password` via bcrypt; not stored from this request |

| API field (response) | Database column   |
|----------------------|-------------------|
| id                   | users.id          |
| name                 | users.name        |
| email                | users.email       |
| phone                | users.phone       |
| role                 | users.role        |
| status               | users.status      |
| last_login           | users.last_login  |
| created_at           | users.created_at  |
| updated_at           | users.updated_at  |

---

### 2.2 Users

| Aspect   | Source | Value / Storage |
|----------|--------|------------------|
| Create   | `POST /users/` | Body: `UserCreate` → stored in `users` |
| List/Get | `GET /users/`, `GET /users/{id}`, etc. | Response: `UserOut` from `users` (no password) |
| Password hash | `GET /users/password-hash?user_id=...` | Response: `UserPasswordResponse` — `password_hash` = `users.password` |

| API (UserCreate) | Database column | Notes |
|------------------|-----------------|-------|
| name             | users.name      | Required |
| email            | users.email     | Optional; unique |
| phone            | users.phone     | Optional; unique |
| password         | users.password  | Stored as **bcrypt hash**, not plain text |
| role             | users.role      | Optional; default customer |

| API (UserOut)    | Database column |
|------------------|-----------------|
| id               | users.id        |
| name             | users.name      |
| email            | users.email     |
| phone            | users.phone     |
| role             | users.role      |
| status           | users.status    |
| last_login       | users.last_login|
| created_at       | users.created_at|
| updated_at       | users.updated_at|

---

### 2.3 Customers

| Aspect | Source | Value / Storage |
|--------|--------|-----------------|
| Create | `POST /customers/` | Body: `CustomerCreate` → stored in `customers` |
| List   | `GET /customers/` | Response: list of `CustomerResponse` from `customers` |
| Get    | `GET /customers/{customer_id}` | Response: `CustomerResponse` from `customers` |

| API (CustomerCreate / CustomerResponse) | Database column |
|----------------------------------------|-----------------|
| shop_name                              | customers.shop_name  |
| owner_name                             | customers.owner_name |
| phone                                  | customers.phone      |
| phone2                                 | customers.phone2     |
| address                                | customers.address    |
| pincode                                | customers.pincode    |
| latitude                               | customers.latitude    |
| longitude                              | customers.longitude  |
| id (response only)                     | customers.id         |
| created_at (response only)             | customers.created_at |

---

### 2.4 Orders

| Aspect | Source | Value / Storage |
|--------|--------|-----------------|
| Create | `POST /orders/` | Body: `OrderCreate` → stored in `orders`; `trays_holding` computed server-side |
| Update | `PUT /orders/{order_id}` | Body: `OrderUpdate` (partial) → `orders`; `trays_holding` recomputed |
| List/Get | `GET /orders/`, `GET /orders/{order_id}`, `GET /orders/customer/{id}` | Response: `OrderResponse` from `orders` |
| Latest holdings | `GET /orders/customer/{customer_id}/latest-holdings` | Response: `OrderLatestHoldingsResponse` — one row from `orders` (latest by `created_at`) |

| API (OrderCreate / OrderUpdate) | Database column   | Notes |
|--------------------------------|-------------------|-------|
| customer_id                    | orders.customer_id|       |
| trays_taken                    | orders.trays_taken|       |
| trays_returned                 | orders.trays_returned |  |
| trays_holding                  | orders.trays_holding  | **Not sent by client.** Computed as trays_taken − trays_returned on create/update. |
| bottles_holding                | orders.bottles_holding| |
| bottles_returned               | orders.bottles_returned| |
| bottles_damaged                | orders.bottles_damaged| |
| payment_status                 | orders.payment_status | |
| delivered_by                   | orders.delivered_by  | |
| review_status                  | orders.review_status | |

| API (OrderResponse)            | Database column   |
|--------------------------------|-------------------|
| order_id                       | orders.order_id   |
| customer_id                    | orders.customer_id|
| trays_taken                    | orders.trays_taken|
| trays_returned                 | orders.trays_returned |
| trays_holding                  | orders.trays_holding  |
| bottles_holding               | orders.bottles_holding|
| bottles_returned               | orders.bottles_returned|
| bottles_damaged               | orders.bottles_damaged|
| payment_status                | orders.payment_status |
| delivered_by                  | orders.delivered_by  |
| review_status                 | orders.review_status  |
| created_at                    | orders.created_at    |

| API (OrderLatestHoldingsResponse) | Database column   |
|-----------------------------------|-------------------|
| order_id                          | orders.order_id   |
| created_at                        | orders.created_at |
| trays_holding                     | orders.trays_holding |
| bottles_holding                  | orders.bottles_holding |
| bottles_damaged                  | orders.bottles_damaged  |

---

### 2.5 Order temp

| Aspect | Source | Value / Storage |
|--------|--------|-----------------|
| Create | `POST /order-temp/` | Body: `OrderTempCreate` → stored in `order_temp`; `trays_holding` computed |
| Update | `PUT /order-temp/{order_id}` | Body: `OrderTempUpdate` → `order_temp`; `trays_holding` recomputed |
| List/Get | `GET /order-temp/`, `GET /order-temp/{order_id}`, etc. | Response: `OrderTempResponse` from `order_temp` |

| API (OrderTempCreate / OrderTempUpdate) | Database column      | Notes |
|----------------------------------------|----------------------|-------|
| customer_id                             | order_temp.customer_id |  |
| trays_taken                             | order_temp.trays_taken  |  |
| trays_returned                          | order_temp.trays_returned| |
| trays_holding                           | order_temp.trays_holding | Computed server-side. |
| bottles_holding                        | order_temp.bottles_holding| |
| bottles_returned                       | order_temp.bottles_returned| |
| bottles_damaged                        | order_temp.bottles_damaged| |
| payment_status                         | order_temp.payment_status | |
| delivered_by                           | order_temp.delivered_by  | |
| review_status                          | order_temp.review_status | |

| API (OrderTempResponse) | Database column        |
|-------------------------|------------------------|
| order_id                | order_temp.order_id    |
| customer_id             | order_temp.customer_id |
| trays_taken             | order_temp.trays_taken |
| trays_returned          | order_temp.trays_returned |
| trays_holding           | order_temp.trays_holding  |
| bottles_holding        | order_temp.bottles_holding |
| bottles_returned       | order_temp.bottles_returned |
| bottles_damaged        | order_temp.bottles_damaged  |
| payment_status         | order_temp.payment_status  |
| delivered_by          | order_temp.delivered_by    |
| review_status         | order_temp.review_status   |
| created_at            | order_temp.created_at      |

---

## 3. Summary

- **Auth:** Login uses `users`; request `identifier`/`password` are not stored; only `last_login` is updated; response is `UserOut` (no password).
- **Users:** Create stores hashed password in `users.password`; all read endpoints return user fields except password.
- **Customers:** Create/response fields map directly to `customers` columns.
- **Orders / order_temp:** Client sends `trays_taken` and `trays_returned`; server computes and stores `trays_holding`. All other request/response fields map directly to the same-named columns in `orders` or `order_temp`.
