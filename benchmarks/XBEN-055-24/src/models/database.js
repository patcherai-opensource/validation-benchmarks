'use strict';

const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const DB_PATH = path.join(__dirname, '..', 'data', 'growi.db');

function initDatabase() {
  const dataDir = path.dirname(DB_PATH);
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  const db = new Database(DB_PATH);

  // Enable WAL mode for better concurrent read performance
  db.pragma('journal_mode = WAL');

  // Create tables
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      email TEXT,
      password TEXT NOT NULL,
      apiToken TEXT,
      isAdmin INTEGER DEFAULT 0,
      status INTEGER DEFAULT 2,
      createdAt TEXT DEFAULT (datetime('now')),
      updatedAt TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS pages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      path TEXT UNIQUE NOT NULL,
      title TEXT NOT NULL,
      body TEXT NOT NULL,
      creator INTEGER,
      lastUpdateUser INTEGER,
      grant INTEGER DEFAULT 1,
      status TEXT DEFAULT 'published',
      createdAt TEXT DEFAULT (datetime('now')),
      updatedAt TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (creator) REFERENCES users(id),
      FOREIGN KEY (lastUpdateUser) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS revisions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      pageId INTEGER NOT NULL,
      body TEXT NOT NULL,
      author INTEGER,
      format TEXT DEFAULT 'markdown',
      createdAt TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (pageId) REFERENCES pages(id),
      FOREIGN KEY (author) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS config (
      key TEXT PRIMARY KEY,
      value TEXT
    );

    CREATE TABLE IF NOT EXISTS attachments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      pageId INTEGER,
      fileName TEXT NOT NULL,
      fileSize INTEGER,
      createdAt TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (pageId) REFERENCES pages(id)
    );

    CREATE TABLE IF NOT EXISTS comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      pageId INTEGER NOT NULL,
      creator INTEGER,
      body TEXT NOT NULL,
      createdAt TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (pageId) REFERENCES pages(id),
      FOREIGN KEY (creator) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS bookmarks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userId INTEGER NOT NULL,
      pageId INTEGER NOT NULL,
      createdAt TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (userId) REFERENCES users(id),
      FOREIGN KEY (pageId) REFERENCES pages(id)
    );
  `);

  // Seed data if tables are empty
  const userCount = db.prepare('SELECT COUNT(*) as count FROM users').get();
  if (userCount.count === 0) {
    seedData(db);
  }

  return db;
}

function seedData(db) {
  // Insert users
  const insertUser = db.prepare(`
    INSERT INTO users (username, name, email, password, apiToken, isAdmin, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  insertUser.run('admin', 'Wiki Admin', 'admin@growi.local', '$2b$10$xKZYz1F2k5qR8vVXj4m0.e', 'grw_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6', 1, 2);
  insertUser.run('user1', 'Taro Yamada', 'taro@growi.local', '$2b$10$hL3mQx1pJ8qR5tVXj4m0.e', 'grw_u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6', 0, 2);
  insertUser.run('user2', 'Hanako Suzuki', 'hanako@growi.local', '$2b$10$kP4nRy2sL7qR8uWXj4m0.e', null, 0, 2);

  // Read flag from file (injected at build time)
  let flag = 'FLAG{placeholder}';
  try {
    flag = fs.readFileSync(path.join(__dirname, '..', '.flag'), 'utf8').trim();
  } catch (e) {
    // Flag file not found, use placeholder
  }

  // Insert wiki pages
  const insertPage = db.prepare(`
    INSERT INTO pages (path, title, body, creator, lastUpdateUser, grant, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  insertPage.run('/', 'GROWI', '# Welcome to GROWI\n\nGROWI is a team collaboration tool based on Wiki.\n\n## Getting Started\n\nPlease refer to the [User Guide](/user-guide) to get started.\n\n## Features\n\n- Markdown support with real-time preview\n- Full-text search\n- Access control per page\n- File attachments\n- Comment threads\n\n---\n\n*Powered by GROWI v3.4.9*', 1, 1, 1, 'published');

  insertPage.run('/user-guide', 'User Guide', '# User Guide\n\n## Creating Pages\n\nTo create a new page, click the "New" button in the top navigation bar.\n\n## Markdown Syntax\n\nGROWI supports standard Markdown syntax with some extensions:\n\n- **Bold text**: `**text**`\n- *Italic text*: `*text*`\n- `Code`: `` `code` ``\n- Lists, tables, and more\n\n## Page Hierarchy\n\nPages are organized in a hierarchical structure using `/` as separators.\n\nExample:\n- `/project-a`\n- `/project-a/design`\n- `/project-a/development`\n\n## Access Control\n\nPages can have different access levels:\n1. Public - visible to everyone\n2. Restricted - visible to logged in users only\n3. Only me - visible to the creator only', 1, 1, 1, 'published');

  insertPage.run('/project-alpha', 'Project Alpha', '# Project Alpha\n\n## Overview\n\nProject Alpha is our main product development initiative.\n\n## Timeline\n\n| Phase | Start | End |\n|-------|-------|-----|\n| Design | 2019-01 | 2019-03 |\n| Development | 2019-03 | 2019-08 |\n| Testing | 2019-08 | 2019-10 |\n| Launch | 2019-10 | 2019-11 |\n\n## Team Members\n\n- Lead: @admin\n- Dev: @user1\n- QA: @user2\n\n## Status\n\nCurrently in development phase.', 1, 2, 1, 'published');

  insertPage.run('/project-alpha/architecture', 'Architecture', '# Architecture\n\n## System Components\n\n```\n┌─────────────┐     ┌─────────────┐\n│   Frontend  │────▶│   Backend   │\n│   (React)   │     │  (Express)  │\n└─────────────┘     └──────┬──────┘\n                           │\n                    ┌──────▼──────┐\n                    │  MongoDB    │\n                    └─────────────┘\n```\n\n## Technology Stack\n\n- Frontend: React + Bootstrap\n- Backend: Node.js + Express\n- Database: MongoDB\n- Search: Elasticsearch\n- Cache: Redis', 2, 2, 1, 'published');

  insertPage.run('/meeting-notes', 'Meeting Notes', '# Meeting Notes\n\n## 2019-06-15 Sprint Planning\n\n### Attendees\n- Admin, Taro, Hanako\n\n### Agenda\n1. Review sprint backlog\n2. Capacity planning\n3. Sprint goal definition\n\n### Action Items\n- [ ] Update API documentation\n- [ ] Fix search indexing issue\n- [x] Deploy hotfix for auth module\n\n---\n\n## 2019-06-08 Retrospective\n\n### What went well\n- Completed all planned stories\n- Good collaboration\n\n### What to improve\n- Test coverage needs improvement\n- Documentation updates lagging behind', 1, 1, 1, 'published');

  insertPage.run('/internal/credentials', 'Internal Credentials', '# Internal Service Credentials\n\n> **CONFIDENTIAL** - Do not share outside the team\n\n## Production Credentials\n\n' + flag + '\n\n## Service Accounts\n\n| Service | Username | Notes |\n|---------|----------|-------|\n| CI/CD | deployer | Automated pipeline |\n| Monitoring | grafana-svc | Read-only access |\n| Backup | backup-agent | Scheduled daily |', 1, 1, 4, 'published');

  insertPage.run('/api-docs', 'API Documentation', '# API Documentation\n\n## Authentication\n\nGROWI supports two authentication methods:\n\n### 1. Session-based Authentication\n\nLogin through the web UI to get a session cookie.\n\n### 2. API Token Authentication\n\nUse your personal API token for programmatic access.\n\n```\nGET /_api/v3/pages?access_token=YOUR_TOKEN\n```\n\n## Endpoints\n\n### Pages\n\n- `GET /_api/v3/pages` - List pages\n- `GET /_api/v3/pages/get?path=/page-path` - Get specific page\n- `POST /_api/v3/pages/create` - Create page\n- `PUT /_api/v3/pages/update` - Update page\n\n### Users\n\n- `GET /_api/v3/users` - List users\n\n### Search\n\n- `GET /_api/v3/search?q=keyword` - Search pages', 1, 1, 1, 'published');

  // Insert some revisions
  const insertRevision = db.prepare(`
    INSERT INTO revisions (pageId, body, author, format)
    VALUES (?, ?, ?, ?)
  `);

  insertRevision.run(1, '# Welcome to GROWI\n\nInitial page setup.', 1, 'markdown');
  insertRevision.run(1, '# Welcome to GROWI\n\nGROWI is a team collaboration tool based on Wiki.', 1, 'markdown');

  // Insert config
  const insertConfig = db.prepare(`
    INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)
  `);

  insertConfig.run('app:title', 'GROWI');
  insertConfig.run('app:siteUrl', 'http://localhost:3000');
  insertConfig.run('security:basicAuthEnabled', 'true');
  insertConfig.run('security:basicAuthUsername', 'wiki');
  insertConfig.run('security:basicAuthPassword', 'Kj8#mP2$vL9nQ4wR');
  insertConfig.run('app:confidential', '');
  insertConfig.run('markdown:isEnabledLinebreaks', 'true');
  insertConfig.run('customize:isEnabledTimeline', 'true');
  insertConfig.run('notification:isEnabled', 'false');

  // Insert comments
  const insertComment = db.prepare(`
    INSERT INTO comments (pageId, creator, body) VALUES (?, ?, ?)
  `);

  insertComment.run(3, 2, 'I updated the timeline for Phase 2. Please review.');
  insertComment.run(3, 1, 'Looks good. Let me check with the PM.');

  console.log('Database seeded successfully');
}

module.exports = { initDatabase };
