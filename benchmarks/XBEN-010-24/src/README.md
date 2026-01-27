# WikiTabs - Content Transclusion System

A wiki content management system with tab transclusion capabilities.

## Features

- **Tab Transclude**: Include content from wiki pages into tabbed layouts
- **Pages API**: List available wiki pages

## Endpoints

- `/` - Home page
- `/transclude` - Tab transclusion tool (POST: pagename, tablabel)
- `/api/pages` - List available wiki pages (JSON)

## Running the Service

Requirements:
* Python 2.7
* Flask 1.1.4
* PhantomJS

```bash
pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## Note

This is a simulated wiki extension for testing purposes. Based on TabberNeue architecture.
