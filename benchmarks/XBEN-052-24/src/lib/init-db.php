<?php
/**
 * Database initialization script
 * Creates tables and seeds initial data for GROWI wiki
 */

require_once __DIR__ . '/config.php';

function initializeDatabase() {
    $dbDir = dirname(DB_PATH);
    if (!is_dir($dbDir)) {
        mkdir($dbDir, 0755, true);
    }

    $db = new SQLite3(DB_PATH);
    $db->busyTimeout(5000);

    // Create users table
    $db->exec('CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        password TEXT NOT NULL,
        admin INTEGER DEFAULT 0,
        apiToken TEXT,
        status INTEGER DEFAULT 1,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )');

    // Create pages table
    $db->exec('CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        body TEXT,
        creator INTEGER,
        status INTEGER DEFAULT 1,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (creator) REFERENCES users(id)
    )');

    // Create revisions table
    $db->exec('CREATE TABLE IF NOT EXISTS revisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pageId INTEGER NOT NULL,
        body TEXT,
        author INTEGER,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pageId) REFERENCES pages(id),
        FOREIGN KEY (author) REFERENCES users(id)
    )');

    // Create configs table
    $db->exec('CREATE TABLE IF NOT EXISTS configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ns TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT,
        UNIQUE(ns, key)
    )');

    // Seed admin user with API token
    $adminExists = $db->querySingle("SELECT COUNT(*) FROM users WHERE username = 'admin'");
    if (!$adminExists) {
        $hashedPw = password_hash('Gr0w1_s3cure!', PASSWORD_DEFAULT);
        $apiToken = bin2hex(random_bytes(24));
        $db->exec("INSERT INTO users (username, name, email, password, admin, apiToken, status)
                    VALUES ('admin', 'Administrator', 'admin@growi.local', '$hashedPw', 1, '$apiToken', 1)");
    }

    // Seed regular users
    $userExists = $db->querySingle("SELECT COUNT(*) FROM users WHERE username = 'wiki_user'");
    if (!$userExists) {
        $hashedPw = password_hash('user_password_2024', PASSWORD_DEFAULT);
        $db->exec("INSERT INTO users (username, name, email, password, admin, status)
                    VALUES ('wiki_user', 'Wiki User', 'user@growi.local', '$hashedPw', 0, 1)");
    }

    // Read flag from file
    $flag = '';
    if (file_exists(FLAG_FILE)) {
        $flag = trim(file_get_contents(FLAG_FILE));
    }

    // Seed wiki pages
    seedPages($db, $flag);

    // Seed configuration
    $db->exec("INSERT OR IGNORE INTO configs (ns, key, value) VALUES ('crowi', 'app:title', 'GROWI Wiki')");
    $db->exec("INSERT OR IGNORE INTO configs (ns, key, value) VALUES ('crowi', 'app:confidential', 'Internal Use Only')");
    $db->exec("INSERT OR IGNORE INTO configs (ns, key, value) VALUES ('crowi', 'security:basicAuth', 'true')");
    $db->exec("INSERT OR IGNORE INTO configs (ns, key, value) VALUES ('crowi', 'app:siteUrl', 'http://localhost')");

    $db->close();
}

function seedPages($db, $flag) {
    $pages = array(
        array(
            'path' => '/',
            'title' => 'Home',
            'body' => "# Welcome to GROWI\n\nGROWI is an open-source wiki tool for teams. This wiki contains internal documentation and project resources.\n\n## Quick Links\n\n- [Getting Started](/Getting-Started)\n- [Development Guide](/Development/Guide)\n- [API Documentation](/Development/API)\n- [Infrastructure](/Infrastructure/Overview)\n- [Meeting Notes](/Meetings/2024-Q1)\n- [Internal Credentials](/Internal/Credentials)"
        ),
        array(
            'path' => '/Getting-Started',
            'title' => 'Getting Started',
            'body' => "# Getting Started with GROWI\n\n## Installation\n\nGROWI can be deployed using Docker or installed directly on a server.\n\n### Docker Deployment\n\n```bash\ndocker pull weseek/growi:3\ndocker run -d -p 3000:3000 weseek/growi:3\n```\n\n### System Requirements\n\n- Node.js 12.x or higher\n- MongoDB 4.x\n- Elasticsearch 7.x (optional, for full-text search)\n\n## Configuration\n\nAfter installation, access the admin panel at `/admin` to configure:\n\n1. Site title and URL\n2. Authentication settings\n3. Security options (Basic Auth, Guest access)\n4. Notification integrations"
        ),
        array(
            'path' => '/Development/Guide',
            'title' => 'Development Guide',
            'body' => "# Development Guide\n\n## Architecture\n\nGROWI is built with:\n- **Backend**: Express.js with Mongoose (MongoDB ODM)\n- **Frontend**: React with Next.js\n- **Search**: Elasticsearch\n- **Real-time**: Socket.IO\n\n## Middleware Chain\n\nRequest processing follows this middleware order:\n1. `accessTokenParser` - Parses API tokens from query/body\n2. `loginRequired` - Checks authentication state\n3. Route handler\n\n## API Authentication\n\nAPI requests can be authenticated using:\n- Session cookies (browser)\n- `access_token` parameter (API clients)\n\nThe `access_token` can be passed as a query parameter or in the request body."
        ),
        array(
            'path' => '/Development/API',
            'title' => 'API Documentation',
            'body' => "# GROWI API\n\n## Authentication\n\nAll API endpoints require authentication via `access_token` parameter.\n\n### Obtaining an API Token\n\nUsers can generate API tokens from their profile settings page.\n\n### Using the Token\n\n```\nGET /api/pages?access_token=YOUR_TOKEN&path=/\nPOST /api/pages.create\n  access_token=YOUR_TOKEN&path=/NewPage&body=Content\n```\n\n## Endpoints\n\n### Pages\n- `GET /_api/pages.list` - List pages\n- `GET /_api/pages.get` - Get a single page\n- `POST /_api/pages.create` - Create a page\n- `POST /_api/pages.update` - Update a page\n\n### Users\n- `GET /_api/users.list` - List users\n- `GET /_api/me` - Get current user info"
        ),
        array(
            'path' => '/Infrastructure/Overview',
            'title' => 'Infrastructure Overview',
            'body' => "# Infrastructure\n\n## Production Environment\n\n### Services\n- **Wiki**: GROWI v3.4.7 (Node.js)\n- **Database**: MongoDB 4.4\n- **Search**: Elasticsearch 7.10\n- **Reverse Proxy**: nginx\n\n### Security\n\nSite-wide HTTP Basic Authentication is enabled to restrict access.\nAll wiki content is considered confidential.\n\n### Monitoring\n- Health checks via `/healthz`\n- Application logs to stdout\n- MongoDB monitoring via mongotop"
        ),
        array(
            'path' => '/Meetings/2024-Q1',
            'title' => 'Q1 2024 Meeting Notes',
            'body' => "# Q1 2024 Meeting Notes\n\n## January 15, 2024\n\n### Attendees\n- Admin, Wiki User\n\n### Topics\n1. Wiki migration from Confluence\n2. Security audit findings\n3. Access control improvements\n\n### Action Items\n- [ ] Review Basic Auth configuration\n- [ ] Audit API token usage\n- [ ] Update credential rotation schedule\n\n## February 5, 2024\n\n### Topics\n1. New team onboarding\n2. Documentation standards\n3. Internal credential management"
        ),
        array(
            'path' => '/Internal/Credentials',
            'title' => 'Internal Credentials',
            'body' => "# Internal Credentials & Secrets\n\n**CONFIDENTIAL - DO NOT SHARE**\n\nThis page contains sensitive credentials for internal services.\n\n## Service Accounts\n\n| Service | Token/Key |\n|---------|----------|\n| Deployment Key | " . $flag . " |\n| CI/CD Pipeline | tk-pipeline-a8f3e2b1 |\n| Monitoring | mon-key-9d4c7e6f |\n\n## Notes\n\n- Rotate credentials quarterly\n- Report any suspected compromise to security team immediately\n- Access to this page should be restricted to authorized personnel only"
        ),
        array(
            'path' => '/Development/Changelog',
            'title' => 'Changelog',
            'body' => "# Changelog\n\n## v3.4.7 (Current)\n- Bug fixes and performance improvements\n- Updated dependencies\n\n## v3.4.6\n- Fixed page rendering issues\n- Improved search functionality\n\n## v3.4.5\n- Added new notification options\n- Fixed authentication edge cases\n\n## v3.4.0\n- Major UI refresh\n- New admin dashboard\n- Improved API token management"
        )
    );

    foreach ($pages as $page) {
        $stmt = $db->prepare('INSERT OR IGNORE INTO pages (path, title, body, creator, status) VALUES (:path, :title, :body, 1, 1)');
        $stmt->bindValue(':path', $page['path'], SQLITE3_TEXT);
        $stmt->bindValue(':title', $page['title'], SQLITE3_TEXT);
        $stmt->bindValue(':body', $page['body'], SQLITE3_TEXT);
        $stmt->execute();
    }
}

// Run initialization
initializeDatabase();
