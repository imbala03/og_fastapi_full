-- Add bottles_taken column to orders and order_temp (for derived bottles_holding = bottles_taken - bottles_returned).
-- Run this on your Render PostgreSQL database if you get 500 on GET /order-temp/ or /orders/.

-- order_temp
ALTER TABLE order_temp ADD COLUMN IF NOT EXISTS bottles_taken INTEGER NOT NULL DEFAULT 0;

-- orders
ALTER TABLE orders ADD COLUMN IF NOT EXISTS bottles_taken INTEGER NOT NULL DEFAULT 0;
