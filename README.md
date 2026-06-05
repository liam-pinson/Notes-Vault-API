# Notes Vault API - Liam Pinson Submission

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

### Pre-requisite: Download the zip and unpackage or clone the repository and open up the directory via terminal.

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
venv\Scripts\activate # Linux: source venv/bin/activate
pip install -r requirements.txt

# Create the .env file to configure the database path
echo "DATABASE_URL=sqlite:///./data/notes.db" > .env

# Start the server
uvicorn app.main:app --reload --env-file .env
```

## How to Run Tests

```bash
python -m venv venv
venv\Scripts\activate # Linux: source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

Tests use an isolated test database that is created fresh before each test and torn down after. No `.env` file or running server is needed — just install dependencies and run the command above. Your real database is never touched.

## How to Test the API

There are three ways to run any request in this documentation:

**Option A — Postman (Recommended):** Import `notes-vault-postman-collection.json` into Postman. Every endpoint is pre-configured with the correct method, headers, and body. The Login request auto-saves your token and the Create Note request auto-saves the note ID — no manual copy-pasting needed. See the [Postman Collection](#postman-collection) section for setup instructions.

**Option B — Git Bash / Mac Terminal:** Copy the `curl` commands exactly as written under each endpoint. The backslash line continuations and single quotes work natively in Git Bash and Mac/Linux terminals. On Windows, open **Git Bash** from the Start menu (installed with Git) and paste the commands directly.

**Option C — Browser Docs:** Visit `http://localhost:8000/docs` while the server is running. FastAPI generates an interactive Swagger UI where you can authorize with your token and run every endpoint directly in the browser without any additional tooling.

> **Windows PowerShell note:** The curl commands as written will not work in PowerShell due to differences in quote handling. Use Git Bash, Postman, or the `/docs` page instead.

---

## Postman Collection

A pre-built Postman collection is included in the repository at `notes-vault-postman-collection.json`. It includes every endpoint with correct methods, headers, request bodies, and expected responses pre-configured.

### How to Import

1. Open Postman
2. Click **Import** in the top left
3. Drag and drop `notes-vault-postman-collection.json` or click **Upload Files** and select it
4. The collection will appear as **Notes Vault API** in your sidebar with all endpoints ready to use

### Environment Setup

The collection uses variables that are populated automatically by scripts — no manual copy-pasting required:

| Variable | Set By | Used By |
|---|---|---|
| `baseUrl` | You set this to `http://localhost:8000` | All requests |
| `token` | Auto-saved after Login | All note endpoints |
| `note_id` | Auto-saved after Create Note | Get, Update, Delete |

Create an environment in Postman called `Notes Vault Local`, add `baseUrl` with value `http://localhost:8000`, and select it from the environment dropdown in the top right before running requests.

### Included Request Folders

- **Health** — Health check endpoint
- **Auth** — Register and Login (Login auto-saves token)
- **Notes** — All five note endpoints (Create auto-saves note ID)
- **Validation Tests** — Pre-built edge case requests showing 401, 422, and 404 responses

---

## Viewing the Database with DB Browser for SQLite

DB Browser for SQLite is a free desktop tool that lets you inspect the database visually as you make API calls — useful for confirming data is being written, updated, and deleted correctly.

### Installation

Download and install from: `https://sqlitebrowser.org/dl/`

### Opening the Database

1. Open DB Browser for SQLite
2. Click **Open Database** in the top toolbar
3. Navigate to your project folder and open `data/notes.db`
4. Click the **Browse Data** tab at the top
5. Use the **Table** dropdown to switch between the `users` and `notes` tables

### Refreshing the View

DB Browser shows a snapshot of the database at the moment you opened it. It does not update live. After each API call, press `Ctrl+R` or go to **File → Revert** to reload the latest data from disk.

### What to Look For

| Table | What you should see |
|---|---|
| `users` | A row per registered user — `id`, `username`, `hashed_password`, `created_at` |
| `notes` | A row per created note — `id`, `title`, `content`, `created_at`, `updated_at`, `owner_id` |

> **Note:** The `hashed_password` column will show a long bcrypt string like `$2b$12$...` — never the raw password. This confirms passwords are stored securely.

---

## End-to-End Walkthrough

A complete run-through of every endpoint in the order a real user would use them. Run these in sequence after starting the server.

> **How to run each step:** Use **Postman** (import `notes-vault-postman-collection.json`), **Git Bash / Mac Terminal** (copy the curl commands as written), or the **browser docs** at `http://localhost:8000/docs`. PowerShell users should use Postman or the browser docs.

> **Viewing the database:** Open `data/notes.db` in DB Browser for SQLite before starting. After each step that creates, updates, or deletes data, press `Ctrl+R` in DB Browser to refresh and confirm the change is reflected on disk.

---

### Step 1 — Confirm the server is running

**Postman:** `GET Health Check` in the Health folder.

**Git Bash / Terminal:**
```bash
curl http://localhost:8000/health
```

**Browser:** Visit `http://localhost:8000/health` directly

Expected response `200 OK`:
```json
{ "status": "ok" }
```

---

### Step 2 — Register a new account

**Postman:** `POST Register` in the Auth folder.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "liam", "password": "securepass123"}'
```

**Browser:** `http://localhost:8000/docs` → `POST /auth/register` → Try it out

Expected response `201 Created`:
```json
{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "username": "liam",
    "created_at": "2024-01-01T00:00:00"
}
```

> **DB Browser:** Press `Ctrl+R` to refresh → open the `users` table → you should see a new row for `liam` with a hashed password in the `hashed_password` column, confirming the user was saved to disk.

**Postman:** `POST Login` in the Auth folder — token saves to `{{token}}` automatically.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -F "username=liam" \
  -F "password=securepass123"
```

**Browser:** `http://localhost:8000/docs` → `POST /auth/token` → Try it out

Expected response `200 OK`:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

> Save the `access_token` value and replace `<your_token>` with it in all steps below. Tokens expire after 30 minutes — re-run this step to get a new one.

---

### Step 4 — Confirm auth is required (no token)

**Postman:** `GET Get Note - No Token (401)` in the Validation Tests folder.

**Git Bash / Terminal:**
```bash
curl http://localhost:8000/notes/
```

**Browser:** `http://localhost:8000/docs` → `GET /notes/` → Try it out (without authorizing)

Expected response `401 Unauthorized` — confirms protected routes are locked without a token:
```json
{
    "detail": "Not authenticated"
}
```

---

### Step 5 — Create your first note

**Postman:** `POST Create Note` in the Notes folder — note ID saves to `{{note_id}}` automatically.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/notes/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Shopping List", "content": "Buy milk, eggs, and bread"}'
```

**Browser:** `http://localhost:8000/docs` → Authorize → `POST /notes/` → Try it out

Expected response `201 Created`:
```json
{
    "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
    "title": "Shopping List",
    "content": "Buy milk, eggs, and bread",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

> Save the `id` value and replace `<note_id>` with it in the steps below.

> **DB Browser:** Press `Ctrl+R` to refresh → open the `notes` table → you should see a new row with the title "Shopping List", the content, and an `owner_id` matching the user ID from Step 2.

**Postman:** `POST Create Note` again with a different body.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/notes/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Work Tasks", "content": "Finish the API project"}'
```

**Browser:** `http://localhost:8000/docs` → Authorize → `POST /notes/` → Try it out

Expected response `201 Created`:
```json
{
    "id": "c3d4e5f6-a7b8-9012-cdef-gh3456789012",
    "title": "Work Tasks",
    "content": "Finish the API project",
    "created_at": "2024-01-01T00:00:01",
    "updated_at": "2024-01-01T00:00:01",
    "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

> **DB Browser:** Press `Ctrl+R` to refresh → open the `notes` table → you should now see two rows, one for each note, both with the same `owner_id`.

**Postman:** `GET List Notes` in the Notes folder.

**Git Bash / Terminal:**
```bash
curl http://localhost:8000/notes/ \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `GET /notes/` → Try it out

Expected response `200 OK` — both notes returned, most recent first:
```json
{
    "total": 2,
    "notes": [
        {
            "id": "c3d4e5f6-a7b8-9012-cdef-gh3456789012",
            "title": "Work Tasks",
            "content": "Finish the API project",
            "created_at": "2024-01-01T00:00:01",
            "updated_at": "2024-01-01T00:00:01",
            "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        },
        {
            "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
            "title": "Shopping List",
            "content": "Buy milk, eggs, and bread",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        }
    ]
}
```

---

### Step 8 — Search notes by keyword

**Postman:** `GET Search Notes` in the Notes folder — change the `search` param value as needed.

**Git Bash / Terminal:**
```bash
curl "http://localhost:8000/notes/?search=milk" \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `GET /notes/` → Try it out → enter `milk` in the search field

Expected response `200 OK` — only the Shopping List note matches, Work Tasks is excluded:
```json
{
    "total": 1,
    "notes": [
        {
            "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
            "title": "Shopping List",
            "content": "Buy milk, eggs, and bread",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        }
    ]
}
```

---

### Step 9 — Get a specific note by ID

**Postman:** `GET Get Note by ID` in the Notes folder — uses `{{note_id}}` automatically.

**Git Bash / Terminal:**
```bash
curl http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `GET /notes/{note_id}` → Try it out → enter note ID

Expected response `200 OK`:
```json
{
    "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
    "title": "Shopping List",
    "content": "Buy milk, eggs, and bread",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### Step 10 — Update a note (partial update)

Only send the fields you want to change. The title is not sent here so it stays unchanged.

**Postman:** `PATCH Update Note` in the Notes folder — uses `{{note_id}}` automatically.

**Git Bash / Terminal:**
```bash
curl -X PATCH http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Buy milk, eggs, bread, and coffee"}'
```

**Browser:** `http://localhost:8000/docs` → Authorize → `PATCH /notes/{note_id}` → Try it out

Expected response `200 OK` — content updated, title unchanged, `updated_at` is now later than `created_at`:
```json
{
    "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
    "title": "Shopping List",
    "content": "Buy milk, eggs, bread, and coffee",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:01:00",
    "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

> **DB Browser:** Press `Ctrl+R` to refresh → open the `notes` table → find the Shopping List row and confirm the `content` column now shows the updated text and `updated_at` is a later timestamp than `created_at`.

**Postman:** `POST Create Note - Empty Content (422)` in the Validation Tests folder.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/notes/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": ""}'
```

**Browser:** `http://localhost:8000/docs` → Authorize → `POST /notes/` → Try it out → send empty content

Expected response `422 Unprocessable Entity` — Pydantic rejects empty content before it reaches the database:
```json
{
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "content"],
            "msg": "String should have at least 1 character"
        }
    ]
}
```

---

### Step 12 — Test authorization isolation (another user cannot access your notes)

Register a second user:

**Postman:** `POST Register` with a different username in the body.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "intruder", "password": "securepass123"}'
```

> **DB Browser:** Press `Ctrl+R` to refresh → open the `users` table → you should now see two rows, one for `liam` and one for `intruder`.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -F "username=intruder" \
  -F "password=securepass123"
```

Try to access the first user's note using the intruder's token:

**Postman:** `GET Get Note by ID` — `{{note_id}}` still points to the first user's note.

**Git Bash / Terminal:**
```bash
curl http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <intruder_token>"
```

Expected response `404 Not Found` — the intruder has a valid token but cannot see another user's notes. The API returns 404 rather than 403 to avoid confirming the note exists at all:
```json
{
    "detail": "Note not found"
}
```

---

### Step 13 — Delete a note

Log back in as `liam` to restore your original token, then:

**Postman:** `POST Login` as `liam` to restore `{{token}}`, then `DELETE Delete Note`.

**Git Bash / Terminal:**
```bash
curl -X DELETE http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `DELETE /notes/{note_id}` → Try it out

Expected response `204 No Content` — no response body returned.

> **DB Browser:** Press `Ctrl+R` to refresh → open the `notes` table → the Shopping List row should be gone. Only the Work Tasks note remains.

**Postman:** `GET Get Note by ID` — should now return 404.

**Git Bash / Terminal:**
```bash
curl http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `GET /notes/{note_id}` → Try it out → enter the deleted note ID

Expected response `404 Not Found` — confirms the note was permanently deleted:
```json
{
    "detail": "Note not found"
}
```

> **DB Browser:** The `notes` table should still show only one row (Work Tasks). The Shopping List row is permanently gone — confirming both the API and the database agree the note no longer exists.

### Register a user

**Postman:** `POST Register` in the Auth folder — body is pre-filled.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "liam", "password": "securepass123"}'
```

**Browser:** `http://localhost:8000/docs` → `POST /auth/register` → Try it out

Expected response `201 Created`:
```json
{
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "username": "liam",
    "created_at": "2024-01-01T00:00:00"
}
```

---

### Get a token

**Postman:** `POST Login` in the Auth folder — token is saved to `{{token}}` automatically after sending.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -F "username=liam" \
  -F "password=securepass123"
```

**Browser:** `http://localhost:8000/docs` → `POST /auth/token` → Try it out

Expected response `200 OK`:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

> Save the `access_token` value — this is your `<your_token>` for all subsequent requests. It expires after 30 minutes, after which you will need to call this endpoint again.

---

### Create a note

**Postman:** `POST Create Note` in the Notes folder — note ID is saved to `{{note_id}}` automatically after sending.

**Git Bash / Terminal:**
```bash
curl -X POST http://localhost:8000/notes/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Shopping", "content": "Buy milk"}'
```

**Browser:** `http://localhost:8000/docs` → Authorize with your token → `POST /notes/` → Try it out

Expected response `201 Created`:
```json
{
    "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
    "title": "Shopping",
    "content": "Buy milk",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

> Save the `id` value — this is your `<note_id>` for get, update, and delete requests.

---

### List all notes

**Postman:** `GET List Notes` in the Notes folder.

**Git Bash / Terminal:**
```bash
curl http://localhost:8000/notes/ \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `GET /notes/` → Try it out

Expected response `200 OK`:
```json
{
    "total": 1,
    "notes": [
        {
            "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
            "title": "Shopping",
            "content": "Buy milk",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        }
    ]
}
```

---

### Search notes

**Postman:** `GET Search Notes` in the Notes folder — change the `search` query param value as needed.

**Git Bash / Terminal:**
```bash
curl "http://localhost:8000/notes/?search=milk" \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `GET /notes/` → Try it out → enter search term

Expected response `200 OK` — returns only notes matching the search term in title or content:
```json
{
    "total": 1,
    "notes": [
        {
            "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
            "title": "Shopping",
            "content": "Buy milk",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        }
    ]
}
```

---

### Get a note by ID

**Postman:** `GET Get Note by ID` in the Notes folder — uses `{{note_id}}` automatically.

**Git Bash / Terminal:**
```bash
curl http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `GET /notes/{note_id}` → Try it out → enter note ID

Expected response `200 OK`:
```json
{
    "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
    "title": "Shopping",
    "content": "Buy milk",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

Returns `404 Not Found` if the note does not exist or belongs to another user:
```json
{
    "detail": "Note not found"
}
```

---

### Update a note

**Postman:** `PATCH Update Note` in the Notes folder — uses `{{note_id}}` automatically.

**Git Bash / Terminal:**
```bash
curl -X PATCH http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated content"}'
```

**Browser:** `http://localhost:8000/docs` → Authorize → `PATCH /notes/{note_id}` → Try it out

Expected response `200 OK` — only the fields you sent are updated, everything else remains unchanged. Notice `updated_at` is now later than `created_at`:
```json
{
    "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
    "title": "Shopping",
    "content": "Updated content",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:01:00",
    "owner_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### Delete a note

**Postman:** `DELETE Delete Note` in the Notes folder — uses `{{note_id}}` automatically.

**Git Bash / Terminal:**
```bash
curl -X DELETE http://localhost:8000/notes/<note_id> \
  -H "Authorization: Bearer <your_token>"
```

**Browser:** `http://localhost:8000/docs` → Authorize → `DELETE /notes/{note_id}` → Try it out

Expected response `204 No Content` — no response body is returned. A subsequent `GET` on the same `<note_id>` will return `404 Not Found`.

---

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
