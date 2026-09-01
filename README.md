# FastAPI Secure API

A FastAPI learning project covering advanced backend concepts from **Phase 1 — Week 3** of the AI Backend roadmap.

## Features

- Sync vs Async HTTP requests
- Concurrent requests with `asyncio.gather`
- Timeout and external request error handling
- JWT authentication
- Password hashing
- Protected endpoints
- Role-Based Access Control (RBAC)
- SQLAlchemy session dependency
- Structured HTTP error responses
- Ruff linting

## Project Structure

```text
fastapi-secure-api/
├── main.py
├── auth.py
├── database.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── .gitignore
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Main Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /sync-fetch` | Synchronous HTTP requests |
| `GET /async-fetch` | Async sequential requests |
| `GET /async-concurrent` | Concurrent HTTP requests |
| `POST /token` | JWT login |
| `GET /users/me` | Protected user endpoint |
| `GET /admin` | Admin-only endpoint |

## Async Benchmark

Example results for 5 external requests:

| Mode | Duration |
|---|---:|
| Sync | ~2.85s |
| Async Sequential | ~1.67s |
| Async Concurrent | ~0.51s |

Concurrent async requests reduce total waiting time for I/O-bound operations.

## Authentication

Login:

```http
POST /token
```

Successful login returns a JWT access token.

Protected endpoints use:

```python
Depends(get_current_user)
```

## RBAC

Two roles are used:

```text
user
admin
```

Expected `/admin` behavior:

```text
No token     → 401
Normal user  → 403
Admin        → 200
```

## Dependency Injection

Database sessions are provided through:

```python
Depends(get_db)
```

The session lifecycle is managed with:

```python
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
```

This ensures the database session is closed after each request.

## Structured Errors

HTTP errors use a consistent format:

```json
{
  "error": {
    "status_code": 403,
    "message": "Admin access required"
  }
}
```

## Quality Check

```bash
python -m ruff check .
```

Expected result:

```text
All checks passed!
```

## Progress

- Day 6 — Async / Sync I/O ✅
- Day 7 — Concurrent Requests ✅
- Day 8 — JWT Authentication ✅
- Day 9 — RBAC ✅
- Day 10 — Dependency Injection & Error Handling ✅

## Status

**Phase 1 — Week 3: Advanced FastAPI**

Final repository review in progress.