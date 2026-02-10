<?php

$flag = getenv('FLAG') ?: 'FLAG{default_flag_for_testing}';

$valid_user = 'admin';
$valid_pass = 'S3cur3W1k1P@ss!';

function check_basic_auth($valid_user, $valid_pass) {
    if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW'])) {
        return false;
    }
    return ($_SERVER['PHP_AUTH_USER'] === $valid_user && $_SERVER['PHP_AUTH_PW'] === $valid_pass);
}

function get_access_token() {
    if (isset($_GET['access_token'])) {
        return $_GET['access_token'];
    }
    if (isset($_POST['access_token'])) {
        return $_POST['access_token'];
    }
    return null;
}

function find_user_by_api_token($token) {
    return null;
}

$authenticated = false;

$access_token = get_access_token();
if ($access_token !== null && is_string($access_token)) {
    $user = find_user_by_api_token($access_token);
    if ($user !== null) {
        $authenticated = true;
    }
    $authenticated = true;
}

if (!$authenticated) {
    if (!check_basic_auth($valid_user, $valid_pass)) {
        header('WWW-Authenticate: Basic realm="Internal Wiki - Authorized Personnel Only"');
        header('HTTP/1.0 401 Unauthorized');
        echo '<!DOCTYPE html><html><head><title>401 Unauthorized</title></head><body><h1>401 Unauthorized</h1><p>Valid credentials required to access this resource.</p></body></html>';
        exit;
    }
    $authenticated = true;
}

$page = isset($_GET['page']) ? $_GET['page'] : 'home';
$allowed_pages = ['home', 'docs', 'admin', 'api-docs'];
if (!in_array($page, $allowed_pages)) {
    $page = 'home';
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TeamDocs Wiki</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
        }
        .nav {
            display: flex;
            gap: 1.5rem;
        }
        .nav a {
            color: white;
            text-decoration: none;
            opacity: 0.9;
            transition: opacity 0.2s;
        }
        .nav a:hover {
            opacity: 1;
        }
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 2rem;
            margin-bottom: 1.5rem;
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 1rem;
            border-bottom: 2px solid #eee;
            padding-bottom: 0.5rem;
        }
        .card h3 {
            color: #444;
            margin: 1.5rem 0 0.5rem 0;
        }
        .card p {
            margin-bottom: 1rem;
        }
        .card ul {
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }
        .card li {
            margin-bottom: 0.5rem;
        }
        .sidebar {
            float: left;
            width: 250px;
            margin-right: 2rem;
        }
        .sidebar-menu {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .sidebar-menu a {
            display: block;
            padding: 0.75rem 1rem;
            color: #333;
            text-decoration: none;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }
        .sidebar-menu a:hover {
            background: #f0f0f0;
        }
        .sidebar-menu a.active {
            background: #667eea;
            color: white;
        }
        .main-content {
            margin-left: 280px;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }
        code {
            background: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
            margin: 1rem 0;
        }
        pre code {
            background: transparent;
            padding: 0;
            color: inherit;
        }
        .alert {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .alert-info {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .alert-warning {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
        }
        .secret-box {
            background: #e8f5e9;
            border: 1px solid #4caf50;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }
        @media (max-width: 768px) {
            .sidebar {
                float: none;
                width: 100%;
                margin-right: 0;
                margin-bottom: 1.5rem;
            }
            .main-content {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">📚 TeamDocs Wiki</div>
        <div class="nav">
            <a href="?page=home">Home</a>
            <a href="?page=docs">Documentation</a>
            <a href="?page=admin">Admin</a>
            <a href="?page=api-docs">API</a>
        </div>
    </div>

    <div class="container">
        <div class="sidebar">
            <div class="sidebar-menu">
                <a href="?page=home" class="<?php echo $page === 'home' ? 'active' : ''; ?>">🏠 Home</a>
                <a href="?page=docs" class="<?php echo $page === 'docs' ? 'active' : ''; ?>">📄 Documentation</a>
                <a href="?page=admin" class="<?php echo $page === 'admin' ? 'active' : ''; ?>">⚙️ Admin Panel</a>
                <a href="?page=api-docs" class="<?php echo $page === 'api-docs' ? 'active' : ''; ?>">🔌 API Reference</a>
            </div>
        </div>

        <div class="main-content">
            <?php if ($page === 'home'): ?>
            <div class="card">
                <h2>Welcome to TeamDocs Wiki</h2>
                <p>TeamDocs is your team's internal knowledge base for documentation, guides, and shared resources. This wiki is protected and only accessible to authorized personnel.</p>
                
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="?page=docs">Getting Started Guide</a></li>
                    <li><a href="?page=api-docs">API Documentation</a></li>
                    <li><a href="?page=admin">System Administration</a></li>
                </ul>

                <h3>Recent Updates</h3>
                <ul>
                    <li>2024-01-15: Updated deployment procedures</li>
                    <li>2024-01-10: Added new API endpoints documentation</li>
                    <li>2024-01-05: Security policy revision</li>
                </ul>
            </div>

            <?php elseif ($page === 'docs'): ?>
            <div class="card">
                <h2>Documentation</h2>
                
                <h3>Overview</h3>
                <p>This section contains technical documentation for our internal systems and processes.</p>

                <h3>Development Guidelines</h3>
                <ul>
                    <li>All code must pass review before merging</li>
                    <li>Follow the established coding standards</li>
                    <li>Write unit tests for new features</li>
                    <li>Update documentation when making changes</li>
                </ul>

                <h3>Deployment Process</h3>
                <p>Our deployment process follows a CI/CD pipeline:</p>
                <ol>
                    <li>Push code to feature branch</li>
                    <li>Create pull request for review</li>
                    <li>Automated tests run on CI</li>
                    <li>After approval, merge to main</li>
                    <li>Automatic deployment to staging</li>
                    <li>Manual promotion to production</li>
                </ol>
            </div>

            <?php elseif ($page === 'admin'): ?>
            <div class="card">
                <h2>Admin Panel</h2>
                
                <div class="alert alert-info">
                    <strong>System Status:</strong> All services operational
                </div>

                <h3>System Configuration</h3>
                <p>Current system settings and configurations are displayed below.</p>

                <h3>Internal Credentials</h3>
                <div class="secret-box">
                    <p><strong>Service Account Token:</strong></p>
                    <code><?php echo htmlspecialchars($flag); ?></code>
                </div>

                <h3>Server Information</h3>
                <ul>
                    <li>Hostname: wiki-prod-01</li>
                    <li>PHP Version: <?php echo phpversion(); ?></li>
                    <li>Memory Limit: <?php echo ini_get('memory_limit'); ?></li>
                </ul>
            </div>

            <?php elseif ($page === 'api-docs'): ?>
            <div class="card">
                <h2>API Reference</h2>
                
                <div class="alert alert-warning">
                    <strong>Note:</strong> API access requires a valid access token. Contact your administrator to obtain API credentials.
                </div>

                <h3>Authentication</h3>
                <p>The API supports token-based authentication. Include your access token as a query parameter:</p>
                <pre><code>GET /api/v1/pages?access_token=YOUR_TOKEN</code></pre>

                <h3>Available Endpoints</h3>
                <ul>
                    <li><code>GET /api/v1/pages</code> - List all pages</li>
                    <li><code>GET /api/v1/pages/:id</code> - Get page by ID</li>
                    <li><code>POST /api/v1/pages</code> - Create new page</li>
                    <li><code>PUT /api/v1/pages/:id</code> - Update page</li>
                    <li><code>DELETE /api/v1/pages/:id</code> - Delete page</li>
                </ul>

                <h3>Example Request</h3>
                <pre><code>curl -X GET "https://wiki.example.com/api/v1/pages?access_token=abc123"</code></pre>
            </div>

            <?php endif; ?>
        </div>
    </div>

    <div class="footer">
        <p>TeamDocs Wiki v2.4.1 | Internal Use Only | © 2024 TeamDocs Inc.</p>
    </div>
</body>
</html>
