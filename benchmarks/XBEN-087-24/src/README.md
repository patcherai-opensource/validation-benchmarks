# DataStream Platform

A server-side rendered data streaming dashboard with client-side hydration for optimal performance.

## Features

- Real-time feedback collection and display
- Server-side rendering with state hydration
- RESTful API for programmatic access
- Progressive data loading

## Development

Requirements:
* Python 2.7
* Flask
* PhantomJS

Run:
```
python -m flask run --host=0.0.0.0 --port=5000
```

## API Endpoints

- `GET /` - Landing page
- `GET /dashboard` - Main dashboard with feedback
- `GET /api/health` - Health check
- `GET /api/feedback` - List feedback entries
- `POST /api/feedback` - Submit new feedback
