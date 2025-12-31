# Render Start Command Configuration

## ✅ Correct Start Command for FastAPI

Your application uses **FastAPI**, not Django/Flask, so you need **uvicorn**, not gunicorn.

### Start Command Options:

**Option 1: With worker (Recommended for free tier)**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

**Option 2: Single process (Simpler, also works)**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Option 3: Using Procfile (Alternative)**
If you want to use Procfile instead:
```bash
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## ❌ Wrong Commands (Don't Use These)

These are for Django/Flask, NOT FastAPI:
- ❌ `gunicorn your_application.wsgi` (Django)
- ❌ `gunicorn app:app` (Flask)
- ❌ `python manage.py runserver` (Django)

---

## How to Set in Render

### Method 1: Using render.yaml (Automatic) ✅

Your `render.yaml` already has the correct command:
```yaml
startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

**If you're using render.yaml, Render will automatically use this command!**

### Method 2: Manual Setup in Render Dashboard

If you're NOT using render.yaml:

1. Go to Render Dashboard → Your Web Service
2. Go to "Settings" tab
3. Find "Start Command" field
4. Enter:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
   ```
5. Save changes

---

## Command Breakdown

- `uvicorn` - ASGI server for FastAPI
- `main:app` - Module name (`main.py`) and app instance (`app`)
- `--host 0.0.0.0` - Listen on all interfaces (required for Render)
- `--port $PORT` - Use Render's PORT environment variable
- `--workers 1` - Single worker (good for free tier, saves memory)

---

## Verification

After setting the start command, check the logs:

1. Go to Render Dashboard → Your Web Service → Logs
2. You should see:
   ```
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:XXXX (Press CTRL+C to quit)
   ```

If you see errors about "gunicorn" or "wsgi", the start command is wrong!

---

## Troubleshooting

### Error: "gunicorn: command not found"
**Cause**: Using gunicorn command for FastAPI app
**Fix**: Change to `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Error: "ModuleNotFoundError: No module named 'uvicorn'"
**Cause**: uvicorn not in requirements.txt
**Fix**: Already in requirements.txt as `uvicorn[standard]` ✅

### Error: "Address already in use"
**Cause**: Not using `$PORT` variable
**Fix**: Always use `--port $PORT` (Render sets this automatically)

---

## Summary

✅ **Correct**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`  
❌ **Wrong**: `gunicorn your_application.wsgi`

Your `render.yaml` already has the correct command, so if Render detects it, you're all set! 🎉

