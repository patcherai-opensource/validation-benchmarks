# DocLoader Pro

Document loading service for AI/ML pipelines.

## Overview

DocLoader Pro is an enterprise-grade document loading service that fetches content from URLs. It supports recursive crawling similar to LangChain's RecursiveUrlLoader.

## API Endpoints

- `POST /api/v1/loader/fetch` - Fetch a document from a URL
- `GET /api/v1/loader/crawl` - Recursively crawl URLs
- `GET /health` - Health check endpoint

## Running

```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=5000
```

## Docker

```bash
docker build -t docloader-pro .
docker run -p 5000:5000 docloader-pro
```
