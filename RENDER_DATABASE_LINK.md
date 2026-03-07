# Render: Use the correct database

If you see **SSL connection has been closed unexpectedly** or connection to a host like `dpg-d43g31ali9vc73d0645g-a`, your Web Service is still using an **old** PostgreSQL instance.

## Fix: Link the new database (og_database_30df)

1. **Render Dashboard** → your **Web Service** (e.g. og-soda-api).
2. Open **Environment** (or **Connections** in some layouts).
3. **DATABASE_URL** is set automatically when a database is linked. To use the new DB:
   - **Option A (recommended):** In **Connections**, unlink the old database and **Link** the PostgreSQL service named **og_database_30df** (host `dpg-d6l1cahaae7s73ft7os0-a`). Render will set `DATABASE_URL` to the **internal** URL.
   - **Option B:** Manually set **DATABASE_URL** to the **Internal** URL of og_database_30df (from the database’s “Info” / “Connections” tab).
4. **Save** and **redeploy** the Web Service.

## Code change (already done)

- `database.py` now appends `?sslmode=require` to any Render PostgreSQL URL, which fixes the “SSL connection has been closed unexpectedly” error once the correct database is linked.
