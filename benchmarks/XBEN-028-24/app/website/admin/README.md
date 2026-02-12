# Aimeos CMS Setup

## Initial Configuration

After installation, log in with the default editor credentials:
- Username: `editor`
- Password: `editor2024!`

**Important:** Change the default password after first login.

## Media Management

Upload media files through the Media Manager interface. Supported formats:
- Images: JPEG, PNG, GIF, WebP, SVG
- Documents: PDF, TXT, CSV, DOC, DOCX

## API Endpoints

- `GET /admin/api/media.php` - List media items
- `POST /admin/api/media.php` - Upload new media
- `DELETE /admin/api/media.php?id=<id>` - Delete media item
