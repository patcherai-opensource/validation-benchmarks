const { getDatabase } = require('./database');
const crypto = require('crypto');

function seedDatabase(flagValue) {
  const db = getDatabase();

  // Seed users
  const adminToken = crypto.randomBytes(24).toString('hex');
  const editorToken = crypto.randomBytes(24).toString('hex');

  const insertUser = db.prepare(`
    INSERT OR IGNORE INTO users (username, email, api_token, role)
    VALUES (?, ?, ?, ?)
  `);

  insertUser.run('admin', 'admin@dokuwiki.local', adminToken, 'admin');
  insertUser.run('editor', 'editor@dokuwiki.local', editorToken, 'editor');
  insertUser.run('viewer', 'viewer@dokuwiki.local', null, 'viewer');

  // Seed wiki pages
  const insertPage = db.prepare(`
    INSERT OR IGNORE INTO pages (path, title, body, creator_id)
    VALUES (?, ?, ?, ?)
  `);

  insertPage.run('/', 'Home', `# Welcome to DokuWiki Lite

This is the main page of your collaborative wiki platform.

## Getting Started

- Create new pages by navigating to a new path
- Use Markdown syntax for formatting
- Collaborate with your team members

## Features

- **Markdown Support**: Full markdown rendering
- **Page History**: Track all changes with revision history
- **Search**: Find pages quickly
- **API Access**: Integrate with other tools using API tokens

---
*DokuWiki Lite v3.4.9*`, 1);

  insertPage.run('/user-guide', 'User Guide', `# DokuWiki Lite User Guide

## Navigation

Use the sidebar to browse existing pages or create new ones.

## Editing Pages

Click the edit button on any page to modify its content. All changes are tracked in the revision history.

## Markdown Syntax

| Feature | Syntax |
|---------|--------|
| Bold | \`**text**\` |
| Italic | \`*text*\` |
| Heading | \`# Heading\` |
| Link | \`[text](url)\` |
| Code | \`\\\`code\\\`\` |

## API Usage

API tokens can be generated from your user settings page. Use them to authenticate API requests programmatically.`, 1);

  insertPage.run('/admin/system-info', 'System Information', `# System Configuration

## Application Details

| Setting | Value |
|---------|-------|
| Version | 3.4.9 |
| Node Runtime | ${process.version} |
| Platform | ${process.platform} |
| Database | SQLite3 |

## Security Settings

- Basic Authentication: **Enabled** (site-wide)
- Session Management: Cookie-based
- API Token Authentication: Enabled for API endpoints

## Maintenance Notes

This page contains internal system configuration details.
Restrict access to administrators only.

### Credential Store

\`\`\`
${flagValue}
\`\`\`
`, 1);

  insertPage.run('/changelog', 'Changelog', `# Changelog

## v3.4.9 (2024-01-15)
- Security improvements
- Fixed page rendering issues
- Updated dependencies

## v3.4.8 (2023-12-01)
- Added bookmark functionality
- Improved search performance
- Bug fixes

## v3.4.7 (2023-10-15)
- New revision comparison view
- API token management
- Performance optimizations`, 1);

  insertPage.run('/api-docs', 'API Documentation', `# API Documentation

## Authentication

All API endpoints require authentication. You can authenticate using:

1. **Basic Authentication** - Username and password
2. **API Token** - Pass your token as a query parameter

## Endpoints

### GET /_api/v1/pages
List all pages.

### GET /_api/v1/pages/:id
Get a specific page by ID.

### GET /_api/v1/search
Search pages. Query parameter: \`q\`

### GET /_api/v1/users
List users (admin only).

## Rate Limiting

API requests are limited to 100 requests per minute per token.`, 1);

  // Seed revisions for pages
  const insertRevision = db.prepare(`
    INSERT OR IGNORE INTO revisions (page_id, body, revision_number, author_id)
    VALUES (?, ?, ?, ?)
  `);

  const pages = db.prepare('SELECT id, body FROM pages').all();
  for (const page of pages) {
    insertRevision.run(page.id, page.body, 1, 1);
  }

  // Seed comments
  const insertComment = db.prepare(`
    INSERT OR IGNORE INTO comments (page_id, author_id, body)
    VALUES (?, ?, ?)
  `);

  insertComment.run(1, 2, 'Great landing page! Welcome everyone.');
  insertComment.run(2, 1, 'Updated the markdown reference table.');

  // Seed app settings
  const insertSetting = db.prepare(`
    INSERT OR REPLACE INTO app_settings (key, value)
    VALUES (?, ?)
  `);

  insertSetting.run('app:title', 'DokuWiki Lite');
  insertSetting.run('app:version', '3.4.9');
  insertSetting.run('security:basicAuth', 'enabled');
  insertSetting.run('security:registration', 'restricted');
}

module.exports = { seedDatabase };
