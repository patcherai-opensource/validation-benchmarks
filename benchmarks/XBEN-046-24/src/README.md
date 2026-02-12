# SafeContent

HTML content sanitization and preview platform.

## Requirements

* Python 3.9+
* PhantomJS
* lxml-html-clean

## Setup

```
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5000
```

## Features

- HTML sanitization using lxml-html-clean
- Live preview rendering via headless browser
- API endpoint for programmatic sanitization
