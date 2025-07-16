# QoE Automation Platform - Setup and Deployment Guide

This guide provides comprehensive instructions for setting up and running the QoE Automation Platform locally and in production.

## Prerequisites

Ensure you have the following installed on your system:

- **Python 3.11+** (https://python.org/downloads/)
- **Node.js 18+** (https://nodejs.org/downloads/)
- **Docker and Docker Compose** (https://docs.docker.com/get-docker/)
- **Git** (https://git-scm.com/downloads/)

## Quick Start (Development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd qoe-automation-platform
```

### 2. Environment Setup

```bash
# Copy environment variables
cp .env.example .env

# Edit .env file with your configuration
# Required variables:
# - OPENAI_API_KEY: Your OpenAI API key for AI features
# - LANGCHAIN_API_KEY: Your LangChain API key (optional)
# - JWT_SECRET_KEY: Change the default secret key
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Wait for services to start (about 30 seconds)
docker-compose logs -f backend

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create a default admin user (optional)
docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.services.user import UserService
from app.schemas.user import UserCreate
from app.models.user import UserRole

db = SessionLocal()
user_service = UserService(db)
admin_user = UserCreate(
    email='admin@qoe-platform.com',
    password='admin123',
    full_name='Admin User',
    role=UserRole.ADMIN
)
user_service.create(admin_user)
db.close()
print('Admin user created: admin@qoe-platform.com / admin123')
"
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Flower (Celery monitoring)**: http://localhost:5555

## Manual Setup (Development)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/qoe_platform"
export REDIS_URL="redis://localhost:6379/0"
export OPENAI_API_KEY="your-openai-key-here"

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.celery_app worker --loglevel=info

# In another terminal, start Celery beat
celery -A app.celery_app beat --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# The frontend will be available at http://localhost:3000
```

### Database Setup

```bash
# Using Docker for PostgreSQL
docker run --name qoe-postgres -e POSTGRES_DB=qoe_platform -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15

# Using Docker for Redis
docker run --name qoe-redis -p 6379:6379 -d redis:7-alpine
```

## Production Deployment

### Using Docker Compose (Recommended)

```bash
# Create production environment file
cp .env.example .env.production

# Edit .env.production with production values
# Important: Change JWT_SECRET_KEY, database passwords, etc.

# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create admin user
docker-compose -f docker-compose.prod.yml exec backend python scripts/create_admin.py
```

### Manual Production Setup

#### Backend Production Setup

```bash
# Install production dependencies
pip install -r requirements.txt
pip install gunicorn

# Set production environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/qoe_platform"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="your-secure-secret-key"
export OPENAI_API_KEY="your-openai-key"
export ENVIRONMENT="production"

# Run migrations
alembic upgrade head

# Start with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Start Celery worker (use supervisor in production)
celery -A app.celery_app worker --loglevel=info

# Start Celery beat
celery -A app.celery_app beat --loglevel=info
```

#### Frontend Production Setup

```bash
# Build the frontend
npm run build

# Serve with nginx or any static file server
# The build files will be in the 'dist' directory
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm test -- --coverage
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/qoe_platform` | Yes |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | `your-secret-key-here-change-in-production` | Yes |
| `OPENAI_API_KEY` | OpenAI API key for AI features | None | Yes |
| `LANGCHAIN_API_KEY` | LangChain API key (optional) | None | No |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` | No |
| `LOG_LEVEL` | Application log level | `INFO` | No |
| `ENVIRONMENT` | Environment name | `development` | No |

### Database Migration

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

## Monitoring and Maintenance

### Health Checks

- **Backend Health**: GET http://localhost:8000/health
- **Celery Health**: http://localhost:5555 (Flower dashboard)
- **Database Health**: Check PostgreSQL connection

### Logs

```bash
# View application logs
docker-compose logs -f backend

# View Celery worker logs
docker-compose logs -f celery-worker

# View frontend logs
docker-compose logs -f frontend

# View all logs
docker-compose logs -f
```

### Backup and Recovery

```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres qoe_platform > backup.sql

# Database restore
docker-compose exec -T postgres psql -U postgres qoe_platform < backup.sql

# File uploads backup
docker-compose exec backend tar -czf /tmp/uploads.tar.gz /app/uploads
docker cp $(docker-compose ps -q backend):/tmp/uploads.tar.gz ./uploads_backup.tar.gz
```

## Performance Optimization

### Database

```sql
-- Add indexes for better performance
CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_adjustments_project_id ON adjustments(project_id);
CREATE INDEX idx_questions_project_id ON questions(project_id);
CREATE INDEX idx_users_email ON users(email);
```

### Caching

```python
# Redis caching is already configured
# Cache frequently accessed data in Redis
```

### Celery Optimization

```bash
# Increase worker concurrency
celery -A app.celery_app worker --concurrency=8

# Use different queues for different tasks
celery -A app.celery_app worker -Q document_processing,adjustment_processing
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # Check database connection
   docker-compose exec postgres psql -U postgres -c "SELECT 1"
   ```

2. **Celery Worker Not Starting**
   ```bash
   # Check Redis connection
   docker-compose exec redis redis-cli ping
   
   # Check Celery configuration
   docker-compose exec backend celery -A app.celery_app inspect stats
   ```

3. **Frontend Build Errors**
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **AI Features Not Working**
   ```bash
   # Check OpenAI API key
   docker-compose exec backend python -c "
   from app.core.config import settings
   print(f'OpenAI API Key: {settings.OPENAI_API_KEY[:10]}...')
   "
   ```

### Debug Mode

```bash
# Enable debug mode
export API_DEBUG=true
export LOG_LEVEL=DEBUG

# View detailed logs
docker-compose logs -f backend | grep DEBUG
```

## Security Considerations

### Production Security

1. **Change default passwords and secrets**
2. **Use HTTPS in production**
3. **Configure proper CORS origins**
4. **Set up proper firewall rules**
5. **Use environment-specific configurations**
6. **Regular security updates**

### SSL/TLS Setup

```nginx
# Nginx configuration for HTTPS
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support

For technical support or questions:

1. Check the application logs
2. Review the troubleshooting section
3. Check the GitHub issues
4. Contact the development team

## License

This project is licensed under the MIT License. See the LICENSE file for details.