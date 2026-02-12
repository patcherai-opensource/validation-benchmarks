# SafeHTML

HTML Content Sanitization Service - policy-based HTML sanitization for web applications.

## Setup

Requirements:
* Python 2.7+
* Flask
* PhantomJS

```
pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## API

- `GET /` - Home page
- `GET/POST /preview` - Interactive HTML sanitization preview
- `POST /api/sanitize` - Programmatic HTML sanitization API
- `GET /about` - About page
- `GET /docs` - API documentation
