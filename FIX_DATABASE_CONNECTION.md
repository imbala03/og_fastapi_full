# Fix: Database Connection Error on Render

## Problem

The application is trying to connect to `localhost` instead of the Render database, causing this error:
```
connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

## Root Cause

The `DATABASE_URL` environment variable is not set. This happens when:
1. The database is not linked to your Web Service
2. The database name in `render.yaml` doesn't match your actual database name

## Solution: Link Your Database in Render

### Step 1: Go to Your Web Service
1. Open [Render Dashboard](https://dashboard.render.com)
2. Click on your Web Service (`og-soda-api`)

### Step 2: Link the Database
1. Go to **Settings** tab
2. Scroll down to **"Connections"** section
3. Click **"Link Database"** or **"Add Database"**
4. Select your PostgreSQL database: **`og_database_0vc9`**
5. Click **"Link"**

### Step 3: Verify Environment Variables
1. Go to **Environment** tab
2. Verify these variables exist:
   - ✅ `DATABASE_URL` - Should be automatically set when database is linked
   - ✅ `ENV` = `staging`
   - ✅ `RENDER` = `"true"`

### Step 4: Redeploy
1. Go to **Manual Deploy** tab
2. Click **"Deploy latest commit"**
3. Or push a new commit to trigger auto-deploy

---

## Alternative: Manual Database URL Setup

If linking doesn't work, manually set `DATABASE_URL`:

1. Go to **Environment** tab
2. Click **"Add Environment Variable"**
3. Set:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://og_user:4cju7zo9oKzqdnDijYWQpIE4fyBQBeGm@dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com/og_database_0vc9`
4. Click **"Save Changes"**
5. Redeploy your service

---

## Verify Database Name in render.yaml

Check that your `render.yaml` has the correct database name:

```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: og_database_0vc9  # ← Make sure this matches your database name
      property: connectionString
```

If your database has a different name, update it in `render.yaml`.

---

## After Fixing

Once the database is linked, you should see in the logs:
```
✅ Database connection established
Environment: staging
Database host: dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com/og_database_0vc9
```

Instead of:
```
❌ connection to server at "localhost" failed
```

---

## Quick Checklist

- [ ] Database is linked in Render dashboard
- [ ] `DATABASE_URL` environment variable exists
- [ ] `ENV=staging` is set
- [ ] Service has been redeployed after linking
- [ ] Check logs to verify connection

---

## Still Having Issues?

1. **Check database status**: Make sure your PostgreSQL database is running
2. **Check database name**: Verify the name matches in `render.yaml`
3. **Check credentials**: Verify database credentials are correct
4. **Check logs**: Look for more detailed error messages

