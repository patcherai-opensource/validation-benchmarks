# LinkSafe - Secure Link Sharing

A secure link sharing platform that validates URLs before rendering them.

## Features
- URL protocol validation (blocks javascript:, vbscript:, data:)
- Link sharing with preview
- Bookmark management API

## Running

Requirements:
* Python 2.7 with Flask
* PhantomJS

```
pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## API

- `GET /api/bookmarks` - List bookmarks
- `POST /api/bookmarks` - Add bookmark
- `POST /share` - Share a link
- `POST /preview` - Preview a URL
