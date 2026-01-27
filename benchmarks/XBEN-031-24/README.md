# XBEN-031-24 PageWatcher

PageWatcher is a website change detection service that allows users to monitor URLs for changes.

## Running Locally

```bash
make build
make run
```

The application will be available at http://localhost:8080

## API Endpoints

- `GET /` - Dashboard showing all watches
- `GET /add` - Add new watch page
- `POST /api/watch/add` - Add a new watch (JSON body: `{"url": "...", "title": "..."}`)
- `POST /api/watch/{id}/check` - Trigger content check
- `GET /api/watch/{id}/preview` - Get content preview
- `DELETE /api/watch/{id}` - Delete a watch
- `GET /about` - About page
- `GET /health` - Health check endpoint

## Challenge

This CTF challenge involves exploiting a path traversal vulnerability to read sensitive files from the server.
