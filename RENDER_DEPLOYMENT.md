# Render Deployment Guide

This guide explains how to deploy the OG Soda FastAPI application to Render.

## Prerequisites

1. A GitHub account with your repository
2. A Render account (free tier available)
3. PostgreSQL database on Render (already created)

## Database Configuration

Your Render PostgreSQL database is already configured:
- **Database Name**: `og_database_0vc9`
- **Username**: `og_user`
- **Host**: `dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com`
- **Port**: `5432`

## Deployment Steps

### 1. Connect GitHub Repository

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub account if not already connected
4. Select your repository: `og_fastapi_full`

### 2. Configure Web Service

Render will automatically detect the `render.yaml` file. If not, use these settings:

**Basic Settings:**
- **Name**: `og-soda-api` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
- `ENV` = `staging`
- `DATABASE_URL` = (will be set automatically when you link the database)

### 3. Link Database

1. In your Web Service settings, go to "Environment" tab
2. Under "Add Environment Variable", click "Link Database"
3. Select your PostgreSQL database: `og_database_0vc9`
4. Render will automatically add `DATABASE_URL` environment variable

### 4. Deploy

1. Click "Create Web Service"
2. Render will start building and deploying your application
3. Monitor the build logs for any issues

## Environment Configuration

The application automatically uses the correct database based on the `ENV` variable:

- **Local Development** (`ENV=dev_local`): Uses local PostgreSQL
- **Render Staging** (`ENV=staging`): Uses Render PostgreSQL

## Post-Deployment

### Verify Deployment

1. Check the health endpoint:
   ```
   https://your-app-name.onrender.com/health
   ```

2. Access API documentation:
   ```
   https://your-app-name.onrender.com/docs
   ```

### Database Tables

The application will automatically create tables on first run using:
```python
Base.metadata.create_all(bind=engine)
```

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Verify the database is linked in Render dashboard
2. Check that `DATABASE_URL` environment variable is set
3. Verify database credentials in Render dashboard

### Build Failures

1. Check `requirements.txt` includes all dependencies
2. Verify Python version compatibility
3. Check build logs for specific error messages

### Application Errors

1. Check application logs in Render dashboard
2. Verify environment variables are set correctly
3. Test database connection using health endpoint

## Free Tier Limitations

Render free tier includes:
- 750 hours/month (enough for 24/7 operation)
- 512 MB RAM
- Limited database connections (pool size adjusted to 5)

## Custom Domain (Optional)

1. In Render dashboard, go to your Web Service
2. Navigate to "Settings" → "Custom Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Monitoring

- **Logs**: Available in Render dashboard under "Logs" tab
- **Metrics**: View in "Metrics" tab
- **Health Checks**: Automatic health checks via `/health` endpoint

## Updating the Application

1. Push changes to your GitHub repository
2. Render will automatically detect and deploy updates
3. Monitor deployment in Render dashboard

## Support

For issues:
1. Check Render documentation: https://render.com/docs
2. Review application logs
3. Test locally first before deploying

