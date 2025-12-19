# Library Management System

A Django REST Framework-based library management application with JWT authentication, comprehensive API, and deployment-ready configuration.

## Features

- **User Authentication**: JWT-based authentication with registration, login, and token refresh
- **Role-Based Access Control**:
  - Anonymous users: Browse books (read-only)
  - Registered users: Browse + Borrow/Return books
  - Administrators: Full access + User management
- **Book Management**: Full CRUD operations with filtering, searching, and pagination
- **Loan Management**: Borrow and return books with due date tracking
- **Admin Panel**: Django admin interface for managing books, users, and loans
- **API Documentation**: Swagger/OpenAPI documentation
- **Security**: CSRF protection, XSS prevention, rate limiting, secure headers
- **Deployment Ready**: Docker and Heroku configuration included

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Authentication**: djangorestframework-simplejwt
- **Database**: SQLite (development), PostgreSQL (production)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Testing**: pytest, pytest-django, pytest-cov
- **Deployment**: Docker, Heroku

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- PostgreSQL (for production)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - API: http://localhost:8000/api/
   - Swagger UI: http://localhost:8000/swagger/
   - Admin Panel: http://localhost:8000/admin/

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Get JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Logout (blacklist token) |
| GET | `/api/auth/profile/` | Get user profile |
| PATCH | `/api/auth/profile/` | Update user profile |

### Books
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/books/` | List books (filterable) | No |
| GET | `/api/books/{id}/` | Get book details | No |
| POST | `/api/books/` | Create book | Admin |
| PUT/PATCH | `/api/books/{id}/` | Update book | Admin |
| DELETE | `/api/books/{id}/` | Delete book | Admin |

### Loans
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/loans/borrow/` | Borrow a book | User |
| POST | `/api/loans/return/` | Return a book | User |
| GET | `/api/loans/history/` | User's loan history | User |
| GET | `/api/loans/active/` | User's active loans | User |
| GET | `/api/loans/admin/` | All loans (admin) | Admin |

### Users (Admin Only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/users/` | List all users |
| GET | `/api/auth/users/{id}/` | Get user details |
| PATCH | `/api/auth/users/{id}/` | Update user |
| DELETE | `/api/auth/users/{id}/` | Deactivate user |

## Filtering and Pagination

### Book Filtering
- `title`: Filter by title (partial match)
- `author`: Filter by author (partial match)
- `isbn`: Filter by exact ISBN
- `genre`: Filter by genre
- `is_available`: Filter by availability (true/false)
- `published_after`: Filter by publication date
- `published_before`: Filter by publication date
- `min_pages`: Filter by minimum page count
- `max_pages`: Filter by maximum page count
- `search`: Full-text search in title, author, ISBN, description
- `ordering`: Sort by title, author, published_date, page_count

### Pagination
All list endpoints return paginated results:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/books/?page=2",
  "previous": null,
  "results": [...]
}
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=accounts --cov=books --cov=loans --cov-report=html

# Run specific test module
pytest accounts/tests/
pytest books/tests/
pytest loans/tests/

# Run with verbose output
pytest -v
```

## Docker Deployment

### Using Docker Compose (Production)

```bash
# Build and start services
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web
```

### Development Mode with Docker

```bash
docker-compose --profile dev up web-dev
```

## Heroku Deployment

1. **Install Heroku CLI and login**
   ```bash
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-library-app
   ```

3. **Add PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DJANGO_ENV=production
   heroku config:set ALLOWED_HOSTS=your-library-app.herokuapp.com
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Run migrations**
   ```bash
   heroku run python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   heroku run python manage.py createsuperuser
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | Django secret key | Required in production |
| `DJANGO_ENV` | Environment (development/production) | `development` |
| `DATABASE_URL` | PostgreSQL connection URL | SQLite in dev |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |

## Project Structure

```
library/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── runtime.txt
├── README.md
├── pytest.ini
├── conftest.py
├── .env.example
├── .gitignore
├── library_project/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── admin.py
│   └── tests/
├── books/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   ├── admin.py
│   └── tests/
└── loans/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    └── tests/
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Token Blacklisting**: Invalidate tokens on logout
- **Rate Limiting**: Protect against brute force attacks
- **CORS**: Configurable cross-origin resource sharing
- **XSS Protection**: Browser XSS filter enabled
- **Content Type Sniffing**: Prevented
- **Clickjacking Protection**: X-Frame-Options set to DENY
- **HTTPS in Production**: SSL redirect enabled
- **HSTS**: HTTP Strict Transport Security headers

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
