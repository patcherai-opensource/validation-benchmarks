<?php
/**
 * DocuWiki - Internal Documentation Platform
 * Version 2.4.1
 */

$flag = getenv('FLAG') ?: 'FLAG{default_flag_for_testing}';

// Configuration
$BASIC_AUTH_USER = 'admin';
$BASIC_AUTH_PASS = 'X9kL#mP2vQ!wR7nJ';

// Access token parser middleware - handles API token authentication
// Tokens are checked against the user database for API access
function parseAccessToken() {
    $access_token = isset($_GET['access_token']) ? $_GET['access_token'] : null;
    if ($access_token === null) {
        $access_token = isset($_POST['access_token']) ? $_POST['access_token'] : null;
    }
    
    if ($access_token === null || !is_string($access_token)) {
        return null;
    }
    
    // Lookup user by API token
    $user = findUserByApiToken($access_token);
    if ($user === null) {
        // No user found for token, continue without setting user
        return 'bypass';
    }
    
    return $user;
}

function findUserByApiToken($token) {
    // In production, this queries the user database
    // Currently no valid API tokens are configured
    return null;
}

// Check if Basic Auth is required for this request
function requiresBasicAuth() {
    // Access token parser runs first - if token param is present, skip basic auth
    $tokenResult = parseAccessToken();
    if ($tokenResult !== null) {
        return false;
    }
    return true;
}

// Verify Basic Authentication credentials
function checkBasicAuth($user, $pass) {
    global $BASIC_AUTH_USER, $BASIC_AUTH_PASS;
    return ($user === $BASIC_AUTH_USER && $pass === $BASIC_AUTH_PASS);
}

// Get current page
$page = isset($_GET['page']) ? $_GET['page'] : 'home';

// Protected pages that require authentication
$protected_pages = ['admin', 'settings', 'users', 'system'];

// Check if current page requires authentication
$is_protected = in_array($page, $protected_pages);

$authenticated = false;
$auth_error = false;

if ($is_protected && requiresBasicAuth()) {
    // Check HTTP Basic Auth
    if (isset($_SERVER['PHP_AUTH_USER']) && isset($_SERVER['PHP_AUTH_PW'])) {
        if (checkBasicAuth($_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW'])) {
            $authenticated = true;
        } else {
            $auth_error = true;
        }
    } else {
        // Send 401 to trigger browser auth dialog
        header('WWW-Authenticate: Basic realm="DocuWiki Admin Area"');
        header('HTTP/1.0 401 Unauthorized');
        echo '<!DOCTYPE html><html><head><title>401 Unauthorized</title></head><body><h1>Authentication Required</h1><p>You must authenticate to access this resource.</p></body></html>';
        exit;
    }
} elseif ($is_protected && !requiresBasicAuth()) {
    // Access token bypass - treat as authenticated
    $authenticated = true;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuWiki - Internal Documentation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6f7; color: #333; line-height: 1.6; }
        .header { background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; }
        .header .version { opacity: 0.7; font-size: 0.8rem; }
        .nav { background: #34495e; padding: 0.5rem 2rem; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 1.5rem; padding: 0.5rem 0; display: inline-block; }
        .nav a:hover { color: #3498db; }
        .nav a.active { border-bottom: 2px solid #3498db; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 2rem; margin-bottom: 1.5rem; }
        .card h2 { color: #2c3e50; margin-bottom: 1rem; border-bottom: 2px solid #3498db; padding-bottom: 0.5rem; }
        .card h3 { color: #34495e; margin: 1.5rem 0 0.5rem; }
        .card p { margin-bottom: 1rem; }
        .card ul { margin-left: 1.5rem; margin-bottom: 1rem; }
        .card li { margin-bottom: 0.5rem; }
        .card code { background: #ecf0f1; padding: 0.2rem 0.5rem; border-radius: 3px; font-family: 'Courier New', monospace; }
        .card pre { background: #2c3e50; color: #ecf0f1; padding: 1rem; border-radius: 5px; overflow-x: auto; margin: 1rem 0; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 1rem 0; }
        .success { background: #d4edda; border-left: 4px solid #28a745; padding: 1rem; margin: 1rem 0; }
        .error { background: #f8d7da; border-left: 4px solid #dc3545; padding: 1rem; margin: 1rem 0; }
        .info { background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 1rem; margin: 1rem 0; }
        .footer { text-align: center; padding: 2rem; color: #7f8c8d; font-size: 0.9rem; }
        table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .badge { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 3px; font-size: 0.8rem; }
        .badge-success { background: #28a745; color: white; }
        .badge-warning { background: #ffc107; color: #333; }
        .badge-danger { background: #dc3545; color: white; }
        .search-box { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📚 DocuWiki</h1>
            <span class="version">v2.4.1 - Internal Documentation Platform</span>
        </div>
        <div>
            <?php if ($authenticated): ?>
                <span>👤 Admin</span>
            <?php endif; ?>
        </div>
    </div>
    
    <div class="nav">
        <a href="?page=home" <?php echo $page === 'home' ? 'class="active"' : ''; ?>>Home</a>
        <a href="?page=docs" <?php echo $page === 'docs' ? 'class="active"' : ''; ?>>Documentation</a>
        <a href="?page=api" <?php echo $page === 'api' ? 'class="active"' : ''; ?>>API Reference</a>
        <a href="?page=changelog" <?php echo $page === 'changelog' ? 'class="active"' : ''; ?>>Changelog</a>
        <a href="?page=admin" <?php echo $page === 'admin' ? 'class="active"' : ''; ?>>⚙️ Admin</a>
    </div>
    
    <div class="container">
        <?php if ($auth_error): ?>
            <div class="error">Invalid credentials. Please try again.</div>
        <?php endif; ?>
        
        <?php if ($page === 'home'): ?>
            <div class="card">
                <h2>Welcome to DocuWiki</h2>
                <p>DocuWiki is your centralized internal documentation platform. Browse our documentation, explore the API, or manage system settings.</p>
                
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="?page=docs">Getting Started Guide</a></li>
                    <li><a href="?page=api">API Documentation</a></li>
                    <li><a href="?page=changelog">Recent Changes</a></li>
                </ul>
                
                <h3>Recent Updates</h3>
                <table>
                    <tr><th>Date</th><th>Page</th><th>Author</th></tr>
                    <tr><td>2024-01-15</td><td>API Authentication</td><td>system</td></tr>
                    <tr><td>2024-01-14</td><td>Installation Guide</td><td>admin</td></tr>
                    <tr><td>2024-01-12</td><td>Troubleshooting</td><td>support</td></tr>
                </table>
            </div>
            
        <?php elseif ($page === 'docs'): ?>
            <div class="card">
                <h2>Documentation</h2>
                <input type="text" class="search-box" placeholder="Search documentation...">
                
                <h3>Installation</h3>
                <p>DocuWiki can be installed using Docker or directly on your server.</p>
                <pre>docker pull docuwiki/docuwiki:latest
docker run -d -p 8080:80 docuwiki/docuwiki</pre>
                
                <h3>Configuration</h3>
                <p>Configuration is managed through environment variables:</p>
                <ul>
                    <li><code>DOCUWIKI_DB_HOST</code> - Database hostname</li>
                    <li><code>DOCUWIKI_DB_NAME</code> - Database name</li>
                    <li><code>DOCUWIKI_ADMIN_EMAIL</code> - Administrator email</li>
                </ul>
                
                <h3>User Management</h3>
                <p>Users can be managed through the admin panel. Access the <a href="?page=admin">Admin Dashboard</a> to manage users, roles, and permissions.</p>
            </div>
            
        <?php elseif ($page === 'api'): ?>
            <div class="card">
                <h2>API Reference</h2>
                
                <h3>Authentication</h3>
                <p>The API supports multiple authentication methods:</p>
                <ul>
                    <li><strong>HTTP Basic Auth</strong> - Standard username/password authentication</li>
                    <li><strong>API Tokens</strong> - Token-based authentication for programmatic access</li>
                </ul>
                
                <div class="info">
                    <strong>Note:</strong> API tokens can be passed via the <code>access_token</code> query parameter or in the request body.
                </div>
                
                <h3>Endpoints</h3>
                <table>
                    <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
                    <tr><td>GET</td><td>/api/pages</td><td>List all pages</td></tr>
                    <tr><td>GET</td><td>/api/pages/{id}</td><td>Get page content</td></tr>
                    <tr><td>POST</td><td>/api/pages</td><td>Create new page</td></tr>
                    <tr><td>PUT</td><td>/api/pages/{id}</td><td>Update page</td></tr>
                    <tr><td>DELETE</td><td>/api/pages/{id}</td><td>Delete page</td></tr>
                </table>
                
                <h3>Example Request</h3>
                <pre>curl -X GET "http://localhost:8080/api/pages" \
     -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ="</pre>
                
                <h3>Rate Limiting</h3>
                <p>API requests are limited to 100 requests per minute per IP address.</p>
            </div>
            
        <?php elseif ($page === 'changelog'): ?>
            <div class="card">
                <h2>Changelog</h2>
                
                <h3>Version 2.4.1 (2024-01-15)</h3>
                <ul>
                    <li>Fixed XSS vulnerability in page comments</li>
                    <li>Updated dependencies</li>
                    <li>Performance improvements</li>
                </ul>
                
                <h3>Version 2.4.0 (2024-01-01)</h3>
                <ul>
                    <li>Added API token authentication</li>
                    <li>New admin dashboard</li>
                    <li>Improved search functionality</li>
                </ul>
                
                <h3>Version 2.3.5 (2023-12-15)</h3>
                <ul>
                    <li>Security patches</li>
                    <li>Bug fixes</li>
                </ul>
                
                <div class="warning">
                    <strong>Security Notice:</strong> Users running versions prior to 2.3.5 should upgrade immediately due to critical security fixes.
                </div>
            </div>
            
        <?php elseif ($page === 'admin' && $authenticated): ?>
            <div class="card">
                <h2>⚙️ Admin Dashboard</h2>
                
                <div class="success">
                    <strong>System Status:</strong> All services operational
                </div>
                
                <h3>System Information</h3>
                <table>
                    <tr><td>Version</td><td>2.4.1</td></tr>
                    <tr><td>PHP Version</td><td><?php echo phpversion(); ?></td></tr>
                    <tr><td>Server</td><td><?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'; ?></td></tr>
                    <tr><td>Uptime</td><td>14 days, 3 hours</td></tr>
                </table>
                
                <h3>Security Configuration</h3>
                <table>
                    <tr><td>Basic Auth</td><td><span class="badge badge-success">Enabled</span></td></tr>
                    <tr><td>SSL/TLS</td><td><span class="badge badge-warning">Not Configured</span></td></tr>
                    <tr><td>Rate Limiting</td><td><span class="badge badge-success">Active</span></td></tr>
                </table>
                
                <h3>Sensitive Configuration</h3>
                <div class="info">
                    <p><strong>System Flag:</strong> <?php echo htmlspecialchars($flag); ?></p>
                </div>
                
                <h3>User Management</h3>
                <table>
                    <tr><th>Username</th><th>Role</th><th>Last Login</th><th>Status</th></tr>
                    <tr><td>admin</td><td>Administrator</td><td>2024-01-15 10:30</td><td><span class="badge badge-success">Active</span></td></tr>
                    <tr><td>editor</td><td>Editor</td><td>2024-01-14 15:45</td><td><span class="badge badge-success">Active</span></td></tr>
                    <tr><td>viewer</td><td>Viewer</td><td>2024-01-10 09:00</td><td><span class="badge badge-warning">Inactive</span></td></tr>
                </table>
            </div>
            
        <?php elseif ($page === 'settings' && $authenticated): ?>
            <div class="card">
                <h2>Settings</h2>
                <p>System settings page.</p>
            </div>
            
        <?php elseif ($page === 'users' && $authenticated): ?>
            <div class="card">
                <h2>User Management</h2>
                <p>User management page.</p>
            </div>
            
        <?php elseif ($page === 'system' && $authenticated): ?>
            <div class="card">
                <h2>System Configuration</h2>
                <p>System configuration page.</p>
            </div>
            
        <?php else: ?>
            <div class="card">
                <h2>Page Not Found</h2>
                <p>The requested page could not be found.</p>
                <p><a href="?page=home">Return to Home</a></p>
            </div>
        <?php endif; ?>
    </div>
    
    <div class="footer">
        <p>DocuWiki v2.4.1 &copy; 2024. Internal use only.</p>
    </div>
</body>
</html>

