# Render Environment Variables Guide

## Quick Answer

**If you're using `render.yaml`**: **NO manual setup needed** - environment variables are automatically configured!

**If you're NOT using `render.yaml`**: **YES, you need to set them manually** in Render dashboard.

---

## Automatic Configuration (Using render.yaml)

If your `render.yaml` file is detected by Render, these environment variables are **automatically set**:

### ✅ Automatically Configured:

1. **`ENV`** = `staging`
   - Tells the app to use staging database configuration
   - Sets connection pool to free tier limits (3 base + 2 overflow)

2. **`RENDER`** = `"true"`
   - Detects that app is running on Render
   - Enables Render-specific optimizations

3. **`DATABASE_URL`** = (Auto-linked from database)
   - **Automatically set when you link your PostgreSQL database**
   - Contains full connection string with credentials
   - **This is the most important variable!**

4. **`PYTHON_VERSION`** = `3.12.0`
   - Specifies Python version for build

### How It Works:

1. Render reads `render.yaml` on deployment
2. Automatically sets the environment variables listed
3. When you link your database, `DATABASE_URL` is automatically added
4. **No manual configuration needed!**

---

## Manual Configuration (Without render.yaml)

If you're NOT using `render.yaml`, you need to manually set these in Render dashboard:

### Required Environment Variables:

1. **`DATABASE_URL`** ⚠️ **REQUIRED**
   - **How to set**: Link your PostgreSQL database in Render dashboard
   - **Value**: Automatically populated when database is linked
   - **Format**: `postgresql://user:password@host:port/database`
   - **Your value**: `postgresql://og_user:4cju7zo9oKzqdnDijYWQpIE4fyBQBeGm@dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com/og_database_0vc9`

2. **`ENV`** (Optional but recommended)
   - **Value**: `staging`
   - **Purpose**: Enables staging optimizations (smaller connection pool)
   - **Default**: If not set, uses `dev_local` (which uses local database URL - will fail!)

3. **`RENDER`** (Optional)
   - **Value**: `"true"`
   - **Purpose**: Enables Render-specific optimizations
   - **Default**: If not set, app still works but may use local settings

### How to Set Manually:

1. Go to Render Dashboard → Your Web Service
2. Click on "Environment" tab
3. Click "Add Environment Variable"
4. Add each variable:
   - Key: `DATABASE_URL`
   - Value: `postgresql://og_user:4cju7zo9oKzqdnDijYWQpIE4fyBQBeGm@dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com/og_database_0vc9`
5. Repeat for `ENV` = `staging` and `RENDER` = `"true"`

---

## Priority Order (How the App Chooses Database URL)

The application checks environment variables in this order:

1. **`DATABASE_URL`** (Highest Priority)
   - If set, uses this directly
   - This is what Render sets when you link the database

2. **`ENV` variable**
   - If `ENV=staging`, uses staging database URL from code
   - If `ENV=dev_local`, uses local database URL (will fail on Render!)

3. **Fallback**
   - Defaults to `dev_local` (will fail on Render!)

---

## Recommended Setup

### ✅ Best Practice (Using render.yaml):

1. **Deploy with `render.yaml`** - Everything is automatic!
2. **Link your database** in Render dashboard
3. **That's it!** No manual environment variables needed

### ⚠️ Alternative (Manual Setup):

If you can't use `render.yaml`:

1. **Link your database** (sets `DATABASE_URL` automatically)
2. **Manually add**:
   - `ENV` = `staging`
   - `RENDER` = `"true"`

---

## Verification

After deployment, check if variables are set:

1. Go to Render Dashboard → Your Web Service → Environment tab
2. You should see:
   - ✅ `DATABASE_URL` (if database is linked)
   - ✅ `ENV` = `staging` (if using render.yaml or manually set)
   - ✅ `RENDER` = `"true"` (if using render.yaml or manually set)

---

## Troubleshooting

### Error: "Database connection failed"

**Cause**: `DATABASE_URL` not set or incorrect

**Solution**:
1. Verify database is linked in Render dashboard
2. Check `DATABASE_URL` exists in Environment tab
3. Verify database credentials are correct

### Error: "Too many database connections"

**Cause**: `ENV` not set to `staging`, using default (larger pool)

**Solution**:
1. Set `ENV` = `staging` in environment variables
2. This enables smaller connection pool (5 max connections)

### App uses wrong database

**Cause**: `ENV` set to `dev_local` or not set

**Solution**:
1. Set `ENV` = `staging` in environment variables
2. Or ensure `DATABASE_URL` is set (takes priority)

---

## Summary

| Setup Method | Manual Env Vars Needed? | Notes |
|-------------|------------------------|-------|
| **With render.yaml** | ❌ **NO** | Everything automatic! |
| **Without render.yaml** | ✅ **YES** | Must set `DATABASE_URL`, `ENV`, `RENDER` |

**Bottom Line**: If you use `render.yaml`, Render handles everything automatically. Just link your database and you're done! 🎉

