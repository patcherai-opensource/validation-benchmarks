# ContentShield - HTML Sanitization Platform

Enterprise-grade HTML content sanitization service.

## Requirements

- Python 3.11+
- Flask

## Running

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5000
```

## API

### POST /api/v1/clean

Sanitize HTML content.

```json
{
  "html": "<p>Your content</p>"
}
```
