# WsgiDAV File Server

A lightweight WebDAV-compatible file server with directory browsing support.

## Features

- Directory browser with file listing and upload
- Configurable realm and display settings
- REST API for server configuration
- Basic authentication support

## Configuration

Server settings can be modified through the web interface at `/server/config` or via the REST API at `/api/config`.

## Running

```
python app.py
```

Server starts on port 5000 by default. Set `FLASK_PORT` environment variable to change.
