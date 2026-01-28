# OpenFAQ - Self-hosted Knowledge Base System

A lightweight FAQ management system for organizations.

## Features

- FAQ article management
- Category organization
- Multi-language support
- Send to friend functionality
- Search functionality
- REST API for integrations

## Installation

Requirements:
* Python 2.7+
* Flask: `pip install Flask`

Run (service will be deployed on port 5000):

```
python app.py
```

## API Endpoints

- `GET /api/categories` - List all categories
- `GET /api/faq/<id>` - Get FAQ article by ID

## Version

v3.1.11 - Open Source FAQ Management System
