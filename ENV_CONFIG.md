# Environment Configuration Guide

This document explains how to configure the application for different environments.

## Environment Variables

The application supports multiple environments through the `ENV` variable:

- `dev_local`: Local development
- `staging`: Render deployment (production)

## Database Configuration

### Development (Local) - `dev_local`

**Environment Variable:**
```env
ENV=dev_local
DATABASE_URL=postgresql://postgres:Bala03@localhost:5432/og_database
```

**Database Credentials:**
- Host: `localhost`
- Port: `5432`
- Database: `og_database`
- Username: `postgres`
- Password: `Bala03`

### Staging (Render) - `staging`

**Environment Variable:**
```env
ENV=staging
DATABASE_URL=postgresql://og_user:4cju7zo9oKzqdnDijYWQpIE4fyBQBeGm@dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com/og_database_0vc9
```

**Database Credentials:**
- Host: `dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com`
- Port: `5432`
- Database: `og_database_0vc9`
- Username: `og_user`
- Password: `4cju7zo9oKzqdnDijYWQpIE4fyBQBeGm`
- Internal Hostname: `dpg-d59qu375r7bs739eiu40-a`

## Setting Up Environment Variables

### Local Development

1. Create a `.env` file in the project root:
```env
ENV=dev_local
DATABASE_URL=postgresql://postgres:Bala03@localhost:5432/og_database
```

2. The application will automatically use these credentials for local development.

### Render Deployment

1. In Render dashboard, go to your Web Service
2. Navigate to "Environment" tab
3. Add environment variables:
   - `ENV` = `staging`
   - `DATABASE_URL` = (automatically set when you link the database)

4. Link your PostgreSQL database:
   - In Render, create or select your PostgreSQL database
   - Link it to your Web Service
   - Render will automatically set `DATABASE_URL`

## Connection Pooling

The application uses different connection pool sizes based on environment:

- **dev_local**: 10 connections, max overflow 20
- **staging**: 5 connections, max overflow 10 (Render limits)

## Security Notes

⚠️ **Important**: Never commit `.env` files or hardcode credentials in source code.

- The `.gitignore` file excludes `.env` files
- Credentials are stored in environment variables
- Render automatically manages database credentials

## Testing Database Connection

You can test the database connection using the health check endpoint:

```bash
curl http://your-app-url/health
```

Or using the database directly:

```bash
# For local development
psql -h localhost -U postgres -d og_database

# For Render staging
PGPASSWORD=4cju7zo9oKzqdnDijYWQpIE4fyBQBeGm psql -h dpg-d59qu375r7bs739eiu40-a.oregon-postgres.render.com -U og_user og_database_0vc9
```

