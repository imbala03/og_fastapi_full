# OG Soda FastAPI Service

FastAPI application for OG Soda order management system.

## Features

- User authentication and authorization
- Customer management
- Order management (orders and temporary orders)
- Admin dashboard
- Agent order tracking
- Health check endpoint

## Environment Setup

### Development (Local)

1. Create a `.env` file in the project root:
```env
ENV=dev_local
DATABASE_URL=postgresql://postgres:Bala03@localhost:5432/og_database
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python runserver.py
```

### Staging (Render)

The application is configured to use Render's PostgreSQL database when deployed.

Environment variables are automatically set by Render:
- `ENV=staging`
- `DATABASE_URL` (from Render database connection)

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Database Environments

- **dev_local**: Local PostgreSQL database
- **staging**: Render PostgreSQL database (production)

## Deployment

### Deploy to Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Render will automatically detect the `render.yaml` configuration
4. The database connection will be automatically configured

## Project Structure

```
.
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── routers/             # API route handlers
├── utils/               # Utility functions
└── requirements.txt     # Python dependencies
```

## Improvements

See `IMPROVEMENTS_SUMMARY.md` for details on recent improvements including:
- Security enhancements
- Error handling
- Connection pooling
- CORS configuration
- Logging

