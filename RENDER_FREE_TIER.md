# Render Free Tier Optimization

This document explains how the application is optimized for Render's free tier hosting.

## Render Free Tier Limitations

- **RAM**: 512 MB
- **CPU**: Shared
- **Database Connections**: 5-10 max connections
- **Spin Down**: Services spin down after 15 minutes of inactivity
- **Hours**: 750 hours/month (enough for 24/7 operation)

## Optimizations Applied

### 1. Database Connection Pooling

**Free Tier Configuration:**
- Pool Size: 3 connections
- Max Overflow: 2 connections
- **Total Maximum**: 5 connections (within free tier limits)

**Local Development:**
- Pool Size: 10 connections
- Max Overflow: 20 connections

This prevents "too many connections" errors on Render's free tier.

### 2. Worker Configuration

- **Workers**: 1 worker (single-threaded)
- **Reason**: Free tier has limited RAM (512 MB), multiple workers would exceed memory limits

### 3. Environment Detection

The application automatically detects Render environment:
- Checks for `RENDER` environment variable
- Uses optimized connection pool when on Render
- Automatically uses `DATABASE_URL` from Render

### 4. Health Check Endpoint

- **Path**: `/health`
- **Purpose**: Keeps service alive and monitors database connectivity
- **Benefit**: Helps prevent unnecessary spin-downs

## Configuration Files

### `render.yaml`
- Specifies free tier plan
- Sets environment variables
- Configures health check
- Links database automatically

### `database.py`
- Auto-detects Render environment
- Uses conservative connection pool
- Handles connection timeouts gracefully

## Deployment Checklist

✅ **Optimized for Free Tier:**
- [x] Connection pool limited to 5 connections
- [x] Single worker configuration
- [x] Health check endpoint configured
- [x] Environment variables properly set
- [x] Database auto-linking configured

## Performance Tips

1. **Cold Starts**: First request after spin-down may take 30-60 seconds
   - This is normal for free tier
   - Subsequent requests are fast

2. **Database Connections**: 
   - Pool is limited to prevent connection errors
   - Connections are reused efficiently

3. **Memory Usage**:
   - Application uses ~200-300 MB RAM
   - Well within 512 MB limit

4. **Response Times**:
   - Normal requests: < 500ms
   - Cold start: 30-60 seconds (first request after inactivity)

## Monitoring

### Check Service Status
```bash
curl https://your-app.onrender.com/health
```

### Expected Response
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Troubleshooting Free Tier Issues

### Issue: Service Spins Down
**Solution**: 
- Use health check endpoint
- Consider upgrading to paid tier for always-on service

### Issue: Database Connection Errors
**Solution**:
- Check connection pool size (should be ≤ 5)
- Verify database is linked in Render dashboard
- Check database status in Render

### Issue: Out of Memory
**Solution**:
- Ensure single worker configuration
- Check for memory leaks in application
- Consider upgrading to paid tier

## Upgrading from Free Tier

If you need:
- **Always-on service**: Upgrade to Starter ($7/month)
- **More RAM**: Upgrade to Standard ($25/month)
- **More database connections**: Upgrade database plan

## Cost Optimization

The current configuration is optimized for **$0/month**:
- Web Service: Free tier
- PostgreSQL Database: Free tier
- Total Cost: **$0/month**

## Notes

- Free tier is perfect for development and low-traffic applications
- For production with high traffic, consider upgrading
- All optimizations maintain full functionality

