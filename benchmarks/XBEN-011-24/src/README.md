# StoreFront Admin Panel

A mock e-commerce administration panel for testing HTML content validation.

## Overview

This is a simplified e-commerce CMS admin panel that allows administrators to create and preview custom HTML content blocks. The application includes HTML validation to prevent XSS attacks.

## Features

- Admin authentication (username: `admin@storefront.local`, password: `admin`)
- Dashboard with statistics
- Product catalog view
- Custom HTML content editor with validation
- Content preview functionality

## Architecture

- **Backend**: Flask (Python 2.7)
- **Frontend**: HTML/CSS (no JavaScript framework)
- **XSS Detection**: PhantomJS

## Content Validation

The application uses a custom HTML validator (`validate_safe_html()`) that:
- Blocks `<script>` tags
- Blocks `javascript:` protocol
- Blocks known event handlers (onclick, onerror, onload, etc.)
- Blocks potentially dangerous tags (iframe, form, input, embed, object)

## Development

To run locally:
```bash
python app.py
```

The application runs on port 5000.

## Endpoints

- `/` - Redirects to admin login
- `/admin/login` - Admin authentication
- `/admin/dashboard` - Overview dashboard
- `/admin/catalog` - Product catalog
- `/admin/content/editor` - Custom HTML editor (POST to save/preview)
- `/admin/orders` - Orders stub
- `/admin/customers` - Customers stub
- `/admin/logout` - Session logout
