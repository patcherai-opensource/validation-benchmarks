<?php
/**
 * NoteHub Wiki Pages and Rendering
 */

// Read flag from file planted at build time
function getWikiFlag() {
    $flagFile = '/var/notehub/data/system-config.dat';
    if (file_exists($flagFile)) {
        return trim(file_get_contents($flagFile));
    }
    return 'FLAG_NOT_SET';
}

function getWikiPages() {
    $flag = getWikiFlag();
    return [
        'home' => [
            'id' => 'pg_001',
            'title' => 'Home',
            'slug' => 'home',
            'content' => "# Welcome to NoteHub\n\nThis is the internal wiki for the development team. Use the navigation to browse pages or search for content.\n\n## Quick Links\n- [Getting Started](/wiki/getting-started)\n- [Architecture Overview](/wiki/architecture)\n- [Deployment Guide](/wiki/deployment-guide)\n- [Admin Panel](/admin)",
            'author' => 'admin',
            'updated_at' => '2024-11-15T10:30:00Z',
            'created_at' => '2024-06-01T08:00:00Z'
        ],
        'getting-started' => [
            'id' => 'pg_002',
            'title' => 'Getting Started',
            'slug' => 'getting-started',
            'content' => "# Getting Started with NoteHub\n\n## Prerequisites\n- Docker and Docker Compose\n- Node.js 18+ (for local development)\n- MongoDB 6.0+\n\n## Installation\n\n```bash\ngit clone https://github.com/internal/notehub.git\ncd notehub\ndocker compose up -d\n```\n\n## First Steps\n1. Navigate to http://localhost:3000\n2. Complete the installer wizard\n3. Create your first wiki page\n\n## API Access\nNoteHub supports API access via session keys. Generate a key from your user profile settings.\n\nAPI endpoints accept the `session_key` parameter for authentication.",
            'author' => 'admin',
            'updated_at' => '2024-10-22T14:15:00Z',
            'created_at' => '2024-06-05T09:00:00Z'
        ],
        'architecture' => [
            'id' => 'pg_003',
            'title' => 'Architecture Overview',
            'slug' => 'architecture',
            'content' => "# Architecture Overview\n\n## Technology Stack\n- **Frontend**: Next.js with React\n- **Backend**: Express.js / PHP\n- **Database**: MongoDB\n- **Search**: Elasticsearch\n\n## Middleware Pipeline\nRequests pass through the following middleware chain:\n1. Rate Limiter\n2. Session Key Parser (API token auth)\n3. Site Authentication (HTTP Basic Auth when enabled)\n4. Route Handler\n\n## Authentication\nNoteHub supports multiple authentication methods:\n- HTTP Basic Authentication (site-wide)\n- LDAP / Active Directory\n- OAuth2 (Google, GitHub)\n- SAML SSO\n\n## API\nAll API endpoints are under `/_api/v1/`. Authentication is handled via session keys passed as query parameters or in the request body.",
            'author' => 'admin',
            'updated_at' => '2024-11-10T16:45:00Z',
            'created_at' => '2024-07-12T11:00:00Z'
        ],
        'deployment-guide' => [
            'id' => 'pg_004',
            'title' => 'Deployment Guide',
            'slug' => 'deployment-guide',
            'content' => "# Deployment Guide\n\n## Production Deployment\n\n### Docker Compose\n```yaml\nservices:\n  app:\n    image: notehub/notehub:latest\n    ports:\n      - '3000:3000'\n    environment:\n      - MONGO_URI=mongodb://mongo:27017/notehub\n      - SITE_AUTH_ENABLED=true\n  mongo:\n    image: mongo:6\n```\n\n### Environment Variables\n| Variable | Description | Default |\n|----------|-------------|---------|\n| MONGO_URI | MongoDB connection string | mongodb://localhost/notehub |\n| SITE_AUTH_ENABLED | Enable site-wide basic auth | false |\n| FILE_UPLOAD | File upload method | local |\n\n## Security Notes\n- Always enable HTTPS in production\n- Configure site-wide authentication for private deployments\n- Rotate API session keys regularly",
            'author' => 'admin',
            'updated_at' => '2024-11-01T09:20:00Z',
            'created_at' => '2024-08-20T13:00:00Z'
        ],
        'internal-credentials' => [
            'id' => 'pg_005',
            'title' => 'Internal Service Credentials',
            'slug' => 'internal-credentials',
            'content' => "# Internal Service Credentials\n\n**CONFIDENTIAL - DO NOT SHARE**\n\nThis page contains internal service credentials for authorized personnel only.\n\n## Production Deployment Key\n```\n" . $flag . "\n```\n\n## Database Access\n- Host: db-prod.internal.notehub.io\n- Port: 27017\n- Read-only user: ro_reporter\n\n## Monitoring\n- Grafana: https://grafana.internal.notehub.io\n- Prometheus: https://prom.internal.notehub.io",
            'author' => 'admin',
            'updated_at' => '2024-11-14T08:00:00Z',
            'created_at' => '2024-09-30T07:00:00Z'
        ]
    ];
}

function getPageList() {
    $pages = getWikiPages();
    $list = [];
    foreach ($pages as $slug => $page) {
        $list[] = [
            'id' => $page['id'],
            'title' => $page['title'],
            'slug' => $page['slug'],
            'author' => $page['author'],
            'updated_at' => $page['updated_at']
        ];
    }
    return ['pages' => $list, 'total' => count($list)];
}

function getPageRevisions($pageId) {
    $pages = getWikiPages();
    foreach ($pages as $page) {
        if ($page['id'] === $pageId) {
            return [
                'revisions' => [
                    ['rev_id' => 'r1', 'author' => $page['author'], 'timestamp' => $page['created_at'], 'message' => 'Initial version'],
                    ['rev_id' => 'r2', 'author' => $page['author'], 'timestamp' => $page['updated_at'], 'message' => 'Updated content']
                ]
            ];
        }
    }
    return ['error' => 'Page not found'];
}

function simpleMarkdownToHtml($markdown) {
    $html = htmlspecialchars($markdown);
    // Headers
    $html = preg_replace('/^### (.+)$/m', '<h3>$1</h3>', $html);
    $html = preg_replace('/^## (.+)$/m', '<h2>$1</h2>', $html);
    $html = preg_replace('/^# (.+)$/m', '<h1>$1</h1>', $html);
    // Bold
    $html = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $html);
    // Code blocks
    $html = preg_replace('/```(\w*)\n(.*?)```/s', '<pre><code>$2</code></pre>', $html);
    // Inline code
    $html = preg_replace('/`([^`]+)`/', '<code>$1</code>', $html);
    // Links
    $html = preg_replace('/\[([^\]]+)\]\(([^)]+)\)/', '<a href="$2">$1</a>', $html);
    // Lists
    $html = preg_replace('/^- (.+)$/m', '<li>$1</li>', $html);
    // Tables (simple)
    $html = preg_replace('/^\|(.+)\|$/m', '<tr><td>$1</td></tr>', $html);
    // Line breaks
    $html = nl2br($html);
    return $html;
}

function renderLayout($title, $bodyContent, $currentSlug = '') {
    $pages = getWikiPages();
    $navItems = '';
    foreach ($pages as $slug => $page) {
        $activeClass = ($slug === $currentSlug) ? ' class="active"' : '';
        $navItems .= '<li' . $activeClass . '><a href="/wiki/' . htmlspecialchars($slug) . '">' . htmlspecialchars($page['title']) . '</a></li>';
    }

    return <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{$title} - NoteHub</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: #fff; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; font-weight: 600; }
        .header h1 a { color: #fff; text-decoration: none; }
        .header nav { display: flex; gap: 16px; align-items: center; }
        .header nav a { color: #bdc3c7; text-decoration: none; font-size: 14px; }
        .header nav a:hover { color: #fff; }
        .search-box { padding: 6px 12px; border: none; border-radius: 4px; font-size: 13px; width: 200px; background: #34495e; color: #ecf0f1; }
        .search-box::placeholder { color: #7f8c8d; }
        .container { display: flex; max-width: 1200px; margin: 0 auto; min-height: calc(100vh - 52px); }
        .sidebar { width: 240px; background: #fff; border-right: 1px solid #e0e0e0; padding: 20px 0; }
        .sidebar h3 { padding: 0 16px; margin-bottom: 12px; font-size: 12px; text-transform: uppercase; color: #999; letter-spacing: 1px; }
        .sidebar ul { list-style: none; }
        .sidebar li { border-left: 3px solid transparent; }
        .sidebar li.active { border-left-color: #3498db; background: #f0f7ff; }
        .sidebar a { display: block; padding: 8px 16px; color: #555; text-decoration: none; font-size: 14px; }
        .sidebar a:hover { background: #f5f5f5; color: #333; }
        .content { flex: 1; padding: 32px 40px; background: #fff; min-width: 0; }
        .content h1 { font-size: 28px; margin-bottom: 16px; color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 8px; }
        .content h2 { font-size: 22px; margin: 24px 0 12px; color: #34495e; }
        .content h3 { font-size: 18px; margin: 20px 0 10px; color: #34495e; }
        .content p, .content li { line-height: 1.7; margin-bottom: 8px; }
        .content pre { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 16px; overflow-x: auto; margin: 12px 0; }
        .content code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 13px; }
        .content pre code { background: none; padding: 0; }
        .content a { color: #3498db; }
        .content table { border-collapse: collapse; margin: 12px 0; width: 100%; }
        .content td, .content th { border: 1px solid #ddd; padding: 8px 12px; }
        .meta { color: #999; font-size: 12px; margin-bottom: 20px; }
        .footer { text-align: center; padding: 16px; color: #999; font-size: 12px; border-top: 1px solid #eee; }
        .alert { background: #fef3cd; border: 1px solid #ffc107; color: #856404; padding: 12px 16px; border-radius: 4px; margin: 16px 0; }
        .search-results { padding: 20px; }
        .search-results .result-item { margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #eee; }
        .search-results .result-item h3 { margin: 0 0 4px; }
        .search-results .result-item p { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1><a href="/">📝 NoteHub</a></h1>
        <nav>
            <form action="/search" method="GET" style="display:inline;">
                <input type="text" name="q" class="search-box" placeholder="Search pages...">
            </form>
            <a href="/_api/v1/pages">API</a>
            <a href="/admin">Admin</a>
        </nav>
    </div>
    <div class="container">
        <div class="sidebar">
            <h3>Pages</h3>
            <ul>{$navItems}</ul>
        </div>
        <div class="content">
            {$bodyContent}
        </div>
    </div>
    <div class="footer">
        NoteHub v2.9.3 &copy; 2024 &mdash; Collaborative Wiki Platform
    </div>
</body>
</html>
HTML;
}

function renderHomePage() {
    $pages = getWikiPages();
    $page = $pages['home'];
    $html = simpleMarkdownToHtml($page['content']);
    $meta = '<div class="meta">Last updated: ' . $page['updated_at'] . ' by ' . htmlspecialchars($page['author']) . '</div>';
    return renderLayout('Home', $meta . $html, 'home');
}

function renderWikiPage($slug) {
    $pages = getWikiPages();
    if (!isset($pages[$slug])) {
        header('HTTP/1.0 404 Not Found');
        return renderNotFoundPage();
    }
    $page = $pages[$slug];
    $html = simpleMarkdownToHtml($page['content']);
    $meta = '<div class="meta">Last updated: ' . $page['updated_at'] . ' by ' . htmlspecialchars($page['author']) . '</div>';
    return renderLayout($page['title'], $meta . $html, $slug);
}

function renderSearchResults($query) {
    if (empty($query)) {
        $body = '<h1>Search</h1><p>Enter a search term to find pages.</p>';
        return renderLayout('Search', $body);
    }
    
    $pages = getWikiPages();
    $results = [];
    foreach ($pages as $slug => $page) {
        if (stripos($page['title'], $query) !== false || stripos($page['content'], $query) !== false) {
            $results[] = $page;
        }
    }
    
    $body = '<h1>Search Results</h1>';
    $body .= '<p>Found ' . count($results) . ' result(s) for "' . htmlspecialchars($query) . '"</p>';
    $body .= '<div class="search-results">';
    foreach ($results as $page) {
        $body .= '<div class="result-item">';
        $body .= '<h3><a href="/wiki/' . htmlspecialchars($page['slug']) . '">' . htmlspecialchars($page['title']) . '</a></h3>';
        $body .= '<p>' . htmlspecialchars(substr($page['content'], 0, 200)) . '...</p>';
        $body .= '</div>';
    }
    $body .= '</div>';
    return renderLayout('Search', $body);
}

function renderAdminPage() {
    $body = '<h1>Administration</h1>';
    $body .= '<div class="alert">Access to admin settings requires administrator privileges.</div>';
    $body .= '<h2>Site Settings</h2>';
    $body .= '<table>';
    $body .= '<tr><td><strong>Site Authentication</strong></td><td>HTTP Basic Auth (Enabled)</td></tr>';
    $body .= '<tr><td><strong>Version</strong></td><td>' . NOTEHUB_VERSION . '</td></tr>';
    $body .= '<tr><td><strong>API Access</strong></td><td>Session Key Authentication</td></tr>';
    $body .= '<tr><td><strong>Total Pages</strong></td><td>' . count(getWikiPages()) . '</td></tr>';
    $body .= '</table>';
    return renderLayout('Admin', $body);
}

function renderUnauthorizedPage() {
    return <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>401 Unauthorized - NoteHub</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; color: #333; }
        .box { text-align: center; padding: 40px; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #e74c3c; margin-bottom: 8px; }
        p { color: #666; }
    </style>
</head>
<body>
    <div class="box">
        <h1>401 Unauthorized</h1>
        <p>Authentication is required to access this NoteHub instance.</p>
        <p style="font-size:12px;color:#999;">NoteHub v2.9.3</p>
    </div>
</body>
</html>
HTML;
}

function renderNotFoundPage() {
    $body = '<h1>Page Not Found</h1><p>The requested page could not be found. <a href="/">Return to home</a>.</p>';
    return renderLayout('Not Found', $body);
}
