# Minimalist Todo API

Production-ready Django REST API with JWT authentication, Google OAuth, email verification, password reset, todo management, rate limiting, and comprehensive API documentation.

## Live Demo

- **API**: https://minimalist-todo-api-luzd.onrender.com
- **Swagger UI**: https://minimalist-todo-api-luzd.onrender.com/api/docs/
- **ReDoc**: https://minimalist-todo-api-luzd.onrender.com/api/redoc/

## Features

- **JWT Authentication** - Token-based auth with refresh tokens and blacklisting
- **Google OAuth** - Sign in with Google
- **Email Verification** - Secure email verification on registration
- **Password Reset** - Token-based password reset with 24-hour expiry
- **Todo Management** - Full CRUD with soft delete and cursor pagination
- **Admin Backoffice** - Superuser-only endpoints for user and todo management
- **Rate Limiting** - IP-based rate limiting on auth endpoints
- **API Documentation** - Auto-generated Swagger UI and ReDoc
- **Custom User Model** - Email-based authentication with additional fields
- **Unit Tests** - 33 comprehensive tests covering auth and todo endpoints
- **Code Quality** - Black, Flake8, Ruff, MyPy configured
- **Docker Ready** - Dockerfile with docker-compose
- **Render Deployment** - Blueprint (`render.yaml`) for one-click deploy
- **Modular Settings** - Separate base, development, and production configs

## Tech Stack

- **Django 5.0.2** - Web framework
- **Django REST Framework 3.14.0** - API framework
- **PostgreSQL** - Primary database
- **djangorestframework-simplejwt 5.3.1** - JWT authentication
- **google-auth 2.27.0** - Google OAuth
- **drf-spectacular 0.27.1** - OpenAPI 3.0 schema generation
- **django-ratelimit** - Rate limiting
- **Docker & Docker Compose** - Containerization
- **Render** - Production hosting

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12 (for local development)

### Docker Setup (Recommended)

```bash
cd django-auth
cp .env.example .env
docker-compose up --build -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
open http://localhost:8000/api/docs/
```

### Local Setup

```bash
pyenv install 3.12.0
pyenv local 3.12.0
python -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt
cp .env.example .env
createdb django_auth_db
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register new user (5 requests/hour)
- `POST /api/auth/login/` - Login and get JWT tokens (10 requests/hour)
- `POST /api/auth/login/google/` - Google OAuth login
- `POST /api/auth/token/refresh/` - Refresh access token (20 requests/hour)
- `POST /api/auth/verify-email/<token>/` - Verify email address
- `POST /api/auth/password-reset/` - Request password reset (3 requests/hour)
- `POST /api/auth/password-reset/confirm/` - Confirm password reset (5 requests/hour)

### User Management

- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile
- `PUT /api/auth/change-password/` - Change password (5 requests/hour)
- `DELETE /api/auth/delete-account/` - Delete account (3 requests/hour)

### Todos (Authenticated)

- `GET /api/todos/` - List todos with cursor pagination (pass `?include_deleted=true` for soft-deleted)
- `POST /api/todos/` - Create a todo
- `GET /api/todos/:id/` - Get single todo
- `PUT /api/todos/:id/` - Full update
- `PATCH /api/todos/:id/` - Partial update (e.g., toggle completed)
- `DELETE /api/todos/:id/` - Soft delete (first call) / permanent delete (second call)

### Admin Backoffice (Superuser Only)

- `GET /api/admin/stats/` - Dashboard statistics (users, todos counts)
- `GET /api/admin/users/` - List all users (pass `?search=` to search by email/username)
- `POST /api/admin/users/` - Create a new user
- `GET /api/admin/users/:id/` - Get user detail
- `PATCH /api/admin/users/:id/` - Update user
- `DELETE /api/admin/users/:id/` - Delete user (cannot delete yourself)
- `GET /api/admin/todos/` - List all todos with user info (pass `?search=` to search by title/body/email)
- `GET /api/admin/todos/:id/` - Get todo detail with user info
- `DELETE /api/admin/todos/:id/` - Permanently delete a todo

### Documentation

- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc documentation
- `GET /api/schema/` - OpenAPI 3.0 schema (JSON)

## Project Structure

```
django-auth/
├── apps/
│   ├── users/              # User management & authentication
│   │   ├── models.py       # Custom User & PasswordResetToken models
│   │   ├── serializers.py  # DRF serializers
│   │   ├── views.py        # API views with rate limiting
│   │   ├── admin_views.py  # Superuser-only admin endpoints
│   │   ├── admin_serializers.py # Admin-specific serializers
│   │   ├── permissions.py  # Custom permissions (IsSuperUser)
│   │   ├── urls.py         # URL routing
│   │   ├── admin_urls.py   # Admin URL routing
│   │   ├── admin.py        # Admin configuration
│   │   └── tests.py        # Unit tests
│   └── todos/              # Todo management
│       ├── models.py       # Todo model
│       ├── serializers.py  # Todo serializer
│       ├── views.py        # CRUD views with ApiResponse wrapper
│       ├── urls.py         # URL routing
│       └── admin.py        # Admin configuration
├── config/
│   ├── settings/
│   │   ├── base.py         # Core settings
│   │   ├── development.py  # Dev settings (CORS allow all)
│   │   └── production.py   # Production settings (security hardened)
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
├── render.yaml             # Render Blueprint (one-click deploy)
├── docker-compose.yml      # Docker services
├── Dockerfile              # Docker build
├── Makefile                # Common commands
├── .flake8                 # Flake8 configuration
├── pyproject.toml          # Black & Ruff configuration
├── mypy.ini                # MyPy configuration
└── pytest.ini              # Pytest configuration
```

## Development

### Docker Commands

```bash
docker-compose up -d              # Start in background
docker-compose logs -f web        # View logs
docker-compose down               # Stop services
docker-compose up --build         # Rebuild after changes
docker-compose exec web bash      # Access container shell
docker-compose exec web pytest -v # Run tests
```

### Code Quality

```bash
make docker-lint                  # Run all checks

# Or individually
docker-compose exec web black apps/ config/
docker-compose exec web ruff check apps/ config/
docker-compose exec web flake8 apps/ config/
docker-compose exec web mypy apps/ config/
```

### Running Tests

```bash
docker-compose exec web pytest -v
pytest --cov=apps --cov-report=html  # With coverage (local)
```

### Database Access

```bash
# Via Docker
docker-compose exec db psql -U postgres -d django_auth_db -c "\dt"
docker-compose exec db psql -U postgres -d django_auth_db -c "SELECT * FROM todos;"
```

## Deployment (Render)

### One-Click Deploy

1. Push code to GitHub
2. Go to Render Dashboard → New → Blueprint
3. Connect your repo — Render detects `render.yaml`
4. Fill in the prompted env vars:
   - `ALLOWED_HOSTS` — your Render service URL (e.g., `minimalist-todo-api-luzd.onrender.com`)
   - `CORS_ALLOWED_ORIGINS` — your frontend URL (e.g., `http://localhost:3000`)
   - `FRONTEND_URL` — your frontend URL
   - `GOOGLE_CLIENT_ID` — Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET` — Google OAuth client secret
5. Deploy — migrations and static files are handled automatically

### Render Blueprint (`render.yaml`)

The blueprint provisions:
- **PostgreSQL database** (free tier, Singapore region)
- **Web service** (Python runtime, gunicorn)
- Auto-generated `SECRET_KEY`
- Auto-linked `DATABASE_URL`

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | Auto-generated | Django secret key |
| `DEBUG` | No | `False` | Debug mode |
| `DJANGO_SETTINGS_MODULE` | Yes | Set in blueprint | Settings module |
| `DATABASE_URL` | Yes | Auto-linked | PostgreSQL connection string |
| `ALLOWED_HOSTS` | Yes | — | Comma-separated hostnames |
| `CORS_ALLOWED_ORIGINS` | Yes | — | Comma-separated frontend URLs |
| `FRONTEND_URL` | No | `http://localhost:3000` | For email links |
| `GOOGLE_CLIENT_ID` | Yes | — | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | — | Google OAuth secret |
| `RATELIMIT_ENABLE` | No | `True` | Enable rate limiting |

## Troubleshooting

**Container won't start:**
```bash
docker-compose logs web
docker-compose down
docker-compose up --build
```

**Database connection issues:**
- Docker: `POSTGRES_HOST=db`
- Local: `POSTGRES_HOST=localhost`
- Check: `docker-compose ps`

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**CORS errors in production:**
- Ensure `CORS_ALLOWED_ORIGINS` is set (no trailing slash)
- `CorsMiddleware` must be first in `MIDDLEWARE`

**Render build fails:**
- Clear build cache: Manual Deploy → Clear build cache & deploy
- Check logs in Render Dashboard → Logs tab

## Future Enhancements

- [ ] Two-factor authentication (2FA)
- [x] ~~Social authentication (Google)~~
- [ ] Social authentication (GitHub)
- [x] ~~Role-based permissions (RBAC)~~
- [ ] Celery for async tasks
- [ ] Redis for caching
- [ ] API versioning
- [ ] Monitoring (Sentry, Prometheus)
- [ ] CI/CD pipeline

## License

MIT

## Author

Evrouin (<elwaycortez@gmail.com>)
