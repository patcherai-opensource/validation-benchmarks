# ContentHub CMS

A modern content management system with flexible layout templates.

## Features

- Multiple layout templates (default, blog, minimal)
- Easy content management
- Enterprise-ready architecture

## Running Locally

```bash
make build
make run
```

The application will be available at http://localhost:8080

## API

- `GET /` - Homepage
- `GET /page/` - Dynamic page with customizable layout
- `GET /about/` - About page
- `GET /contact/` - Contact page

## Layout Customization

The `/page/` endpoint supports the following query parameters:

- `layout` - Template layout name (default, blog, minimal)
- `title` - Page title
- `content` - Page content

Example: `/page/?layout=blog&title=My+Post&content=Hello+World`
