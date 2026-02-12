# eZ Platform Content Management

A lightweight content management platform with RichText editing capabilities.

## Requirements

* Python 2.7+
* Flask
* PhantomJS (for content preview rendering)

## Running

```bash
python -m flask run --host=0.0.0.0 --port=5000
```

## Architecture

- SQLite database for content storage
- DocBook XML-based RichText field type
- Schematron-based content validation
- Session-based authentication with role-based access control
