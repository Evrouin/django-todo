# Django Authentication API

Production-ready Django REST API with JWT authentication, email verification, password reset, rate limiting, and comprehensive API documentation.

## Features

- **JWT Authentication** - Token-based auth with refresh tokens and blacklisting
- **Email Verification** - Secure email verification on registration
- **Password Reset** - Token-based password reset with 24-hour expiry
- **Rate Limiting** - IP-based rate limiting on all auth endpoints
- **API Documentation** - Auto-generated Swagger UI and ReDoc
- **Custom User Model** - Email-based authentication with additional fields
- **Unit Tests** - 15 comprehensive tests covering all endpoints
- **Code Quality** - Black, Flake8, Ruff, MyPy configured
- **Docker Ready** - Multi-stage Dockerfile with docker-compose
- **Modular Settings** - Separate base, development, and production configs

## Tech Stack

- **Django 5.0.2** - Web framework
- **Django REST Framework 3.14.0** - API framework
- **PostgreSQL** - Primary database
- **djangorestframework-simplejwt 5.3.1** - JWT authentication
- **drf-spectacular 0.27.1** - OpenAPI 3.0 schema generation
- **django-ratelimit** - Rate limiting
- **Docker & Docker Compose** - Containerization

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12 (for local development)

### Docker Setup (Recommended)

```bash
# Clone and navigate to project
cd django-auth

# Copy environment file
cp .env.example .env

# Build and start services
docker-compose up --build -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access the API
open http://localhost:8000/api/docs/
```

### Local Setup

```bash
# Install Python 3.12
pyenv install 3.12.0
pyenv local 3.12.0

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/development.txt

# Update .env to use localhost
cp .env.example .env
# Change DATABASE_URL to: postgresql://postgres:postgres@localhost:5432/django_auth_db

# Create database
createdb django_auth_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register new user (5 requests/hour)
- `POST /api/auth/login/` - Login and get JWT tokens (10 requests/hour)
- `POST /api/auth/token/refresh/` - Refresh access token (20 requests/hour)
- `POST /api/auth/verify-email/<token>/` - Verify email address
- `POST /api/auth/password-reset/` - Request password reset (3 requests/hour)
- `POST /api/auth/password-reset/confirm/` - Confirm password reset (5 requests/hour)

### User Management

- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile
- `PUT /api/auth/change-password/` - Change password (5 requests/hour)
- `DELETE /api/auth/delete-account/` - Delete account (3 requests/hour)

### Documentation

- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc documentation
- `GET /api/schema/` - OpenAPI 3.0 schema (JSON)

## Project Structure

```
django-auth/
├── apps/
│   └── users/              # User management app
│       ├── models.py       # Custom User & PasswordResetToken models
│       ├── serializers.py  # DRF serializers
│       ├── views.py        # API views with rate limiting
│       ├── urls.py         # URL routing
│       ├── admin.py        # Admin configuration
│       └── tests.py        # Unit tests
├── config/
│   ├── settings/
│   │   ├── base.py         # Core settings
│   │   ├── development.py  # Dev settings
│   │   └── production.py   # Production settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI entry point
│   └── asgi.py             # ASGI entry point
├── requirements/
│   ├── base.txt            # Core dependencies
│   ├── development.txt     # Dev tools (black, ruff, mypy, pytest)
│   └── production.txt      # Production dependencies
├── scripts/
│   ├── entrypoint.sh       # Docker entrypoint
│   ├── format_code.sh      # Auto-format with black
│   └── check_code.sh       # Run all linters
├── docker-compose.yml      # Docker services
├── Dockerfile              # Multi-stage build
├── Makefile                # Common commands
├── .flake8                 # Flake8 configuration
├── pyproject.toml          # Black & Ruff configuration
├── mypy.ini                # MyPy configuration
└── pytest.ini              # Pytest configuration
```

## Development

### Docker Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build

# Run Django commands
docker-compose exec web python manage.py <command>

# Access container shell
docker-compose exec web bash

# Run tests
docker-compose exec web pytest -v

# Django shell
docker-compose exec web python manage.py shell
```

### Code Quality

```bash
# Format code
docker-compose exec web black apps/ config/

# Check with Ruff
docker-compose exec web ruff check apps/ config/

# Check with Flake8
docker-compose exec web flake8 apps/ config/

# Type check with MyPy
docker-compose exec web mypy apps/ config/

# Run all checks
make docker-lint

# Or locally
source venv/bin/activate
./scripts/format_code.sh
./scripts/check_code.sh
```

### Running Tests

```bash
# Docker
docker-compose exec web pytest -v

# Local
source venv/bin/activate
pytest -v

# With coverage
pytest --cov=apps --cov-report=html
```

### Creating New Apps

```bash
# Docker
docker-compose exec web python manage.py startapp appname
mv appname apps/

# Update apps/appname/apps.py
# Change: name = 'apps.appname'

# Add to INSTALLED_APPS in config/settings/base.py
# 'apps.appname',

# Restart
docker-compose restart web
```

## Environment Variables

Key variables in `.env`:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/django_auth_db
POSTGRES_DB=django_auth_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Email (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Rate Limiting
RATELIMIT_ENABLE=True

# Security (production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Testing the API

Use the included test script:

```bash
chmod +x test_api.sh
./test_api.sh
```

Or test manually with curl:

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Get profile (use access token from login)
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Production Deployment

1. **Generate secure SECRET_KEY**:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

2. **Update environment variables**:
   - Set `DEBUG=False`
   - Set `DJANGO_SETTINGS_MODULE=config.settings.production`
   - Configure `ALLOWED_HOSTS`
   - Set up email backend (SMTP)
   - Use managed PostgreSQL

3. **Security settings** (already configured in production.py):
   - SSL redirect
   - Secure cookies
   - HSTS headers
   - XSS protection
   - Content type sniffing protection

4. **Static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Database migrations**:
   ```bash
   python manage.py migrate --noinput
   ```

6. **Use production WSGI server** (gunicorn already in requirements):
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

## Troubleshooting

**Container won't start:**
```bash
docker-compose logs web
docker-compose down
docker-compose up --build
```

**Database connection issues:**
- Verify `POSTGRES_HOST` in `.env` (`db` for Docker, `localhost` for local)
- Check database is running: `docker-compose ps`

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Module not found:**
- Rebuild: `docker-compose up --build`
- Check app name in `apps.py` matches path

## Future Enhancements

- [ ] Two-factor authentication (2FA)
- [ ] Social authentication (Google, GitHub)
- [ ] Role-based permissions (RBAC)
- [ ] Celery for async tasks
- [ ] Redis for caching
- [ ] WebSocket support
- [ ] API versioning
- [ ] Monitoring (Sentry, Prometheus)
- [ ] CI/CD pipeline
- [ ] Kubernetes deployment

## License

MIT

## Author

Evrouin (elwaycortez@gmail.com)
