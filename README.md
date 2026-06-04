# Notes Vault API

A secure REST API for creating and managing personal notes, built with FastAPI and SQLite.

## System Overview

Notes Vault is a backend service that allows authenticated users to create, read, update, delete, and search personal notes. Each user can only access their own notes. Authentication is handled via JWT tokens and all passwords are hashed using bcrypt.

```
Request → FastAPI → JWT Auth → CRUD Layer → SQLite Database
```

## Tech Choices

| Technology | Purpose | Why |
|---|---|---|
| FastAPI | Web framework | Automatic validation, docs generation, dependency injection |
| SQLAlchemy | ORM | Database-agnostic queries, easy migration to PostgreSQL |
| SQLite | Database | Zero external dependencies, file-based, sufficient for this scale |
| Pydantic | Validation | Request/response validation with clear error messages |
| python-jose | JWT tokens | Stateless authentication without session storage |
| passlib + bcrypt | Password hashing | Industry standard, intentionally slow to resist brute force |
| pytest + httpx | Testing | API-level and unit testing with isolated test database |
| Docker | Containerization | Consistent environment, single command startup |

## How to Run

### Option 1 — Docker (Recommended, no Python required)

No additional configuration needed — the database path is set automatically via Docker Compose.

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

To stop:
```bash
docker-compose down
```

### Option 2 — Local

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create the .env file to configure the database path
echo "DATABASE_URL=sqlite:///./data/notes.db" > .env

# Start the server
uvicorn app.main:app --reload --env-file .env
```

## How to Run Tests

```bash
pytest tests/ -v
```

Tests use an isolated test database that is created fresh before each test and torn down after. No `.env` file or running server is needed — just install dependencies and run the command above. Your real database is never touched.

## API Usage Examples

> Replace `<your_token>` with the token returned from `POST /auth/token`, and `<note_id>` with the UUID returned from `POST /notes/`. The interactive API docs at `http://localhost:8000/docs` can also be used to test all endpoints directly in the browser.

### Register a user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "liam", "password": "securepass123"}'
```

### Get a token

```bash
curl -X POST http://localhost:8000/auth/token \
  -F "username=liam" \
  -F "password=securepass123"
```

### Create a note

```bash
curl -X POST http://localhost:8000/notes/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Shopping", "content": "Buy milk"}'
```

### List all notes

```bash
curl http://localhost:8000/notes/ \
  -H "Authorization: Bearer <your_token>"
```

### Search notes

```bash
curl "http://localhost:8000/notes/?search=milk" \
  -H "Authorization: Bearer <your_token>"
```

### Get a note by ID

```bash
curl http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>"
```

### Update a note

```bash
curl -X PATCH http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated content"}'
```

### Delete a note

```bash
curl -X DELETE http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>"
```

## API Response Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Resource created |
| 204 | Success, no content (delete) |
| 400 | Bad request (e.g. duplicate username) |
| 401 | Unauthorized (missing or invalid token) |
| 404 | Resource not found |
| 422 | Validation error (e.g. empty content) |

## Assumptions and Tradeoffs

**SQLite over PostgreSQL** — SQLite requires zero external dependencies making local setup and review frictionless. The SQLAlchemy ORM means switching to PostgreSQL later requires only changing the `DATABASE_URL` environment variable.

**JWT over sessions** — Stateless authentication means no session storage is needed. Tokens expire after 30 minutes. A production system would add refresh tokens.

**404 instead of 403 on other users notes** — When a user tries to access a note that exists but belongs to someone else, the API returns 404 rather than 403. This avoids leaking information about whether a note ID exists at all.

**UUID primary keys** — Prevents ID enumeration attacks. Users cannot probe sequential IDs to discover other users notes.

**Hardcoded SECRET_KEY** — For this challenge the JWT secret is hardcoded. In production this must be an environment variable, rotated regularly, and never committed to version control.

**Environment configuration via .env** — The DATABASE_URL is configured via a .env file locally to ensure both local and Docker environments target the same database file at `data/notes.db`. In production all environment variables should be injected by the deployment platform and never committed to version control.

**bcrypt and passlib versions pinned** — These two libraries have a known version compatibility issue with newer bcrypt releases. Requirements are pinned to `bcrypt==4.0.1` and `passlib==1.7.4` to ensure consistent behavior across environments.

## Future Improvements

- Move `SECRET_KEY` to environment variable via `pydantic-settings`
- Add refresh tokens so users are not logged out after 30 minutes
- Add pagination to `GET /notes/` for large note collections
- Switch to PostgreSQL for production deployments
- Add rate limiting to auth endpoints to prevent brute force attacks
- Add note tagging and filtering by tag
- Add request ID tracing and structured logging for better observability in production