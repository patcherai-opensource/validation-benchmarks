# Onyx - Enterprise Knowledge Management

A document management and search platform with user group-based access controls.

## Quick Start

```bash
make build
make run
```

The application will be available at `http://localhost:8080`.

## Architecture

- **FastAPI** backend with SQLite database
- **JWT-based** authentication
- **Group-based** access control for documents and connector-credential pairs
- **Role hierarchy**: basic → curator → admin

## API Endpoints

- `POST /api/auth/login` - Authenticate and receive JWT token
- `GET /api/me` - Get current user info
- `GET /api/search` - Search accessible documents
- `GET /api/manage/users` - List users (curator/admin)
- `GET /api/manage/admin/user-group` - List user groups (curator/admin)
- `GET /api/manage/admin/user-group/{id}` - Get user group details
- `PATCH /api/manage/admin/user-group/{id}` - Update user group
- `GET /api/manage/connector-credential-pairs` - List connector-credential pairs
