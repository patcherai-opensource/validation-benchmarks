# Pimcore Asset Manager

A digital asset management system inspired by Pimcore CMS.

## Setup

You need `docker` and `docker-compose`.

```
make build
make run
```

## Challenge

The challenge will be available at: http://localhost:5000

This is a Pimcore-style Asset Management System with an admin panel for managing digital assets.

## Endpoints

- `/` - Dashboard
- `/admin/assets` - Asset library with list of all assets  
- `/admin/assets/download-as-zip` - Download manager page
- `/admin/assets/download-as-zip-add-files` - API endpoint for preparing assets for download
- `/api/system/info` - System information

## Database

The application uses SQLite with two tables:
- `assets` - Contains digital asset metadata (id, filename, filepath, mimetype, filesize)
- `system_config` - Contains system configuration settings
