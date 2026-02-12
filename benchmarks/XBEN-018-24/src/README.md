# ContentGuard CMS

A content management system with integrated HTML sanitization.

## Setup

Requirements:
- Python 3.9+
- PhantomJS (for content rendering verification)

```
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5000
```

## Features

- HTML content composition and preview
- Automatic HTML sanitization for user-submitted content
- Content verification through headless browser rendering
- REST API for programmatic content management
