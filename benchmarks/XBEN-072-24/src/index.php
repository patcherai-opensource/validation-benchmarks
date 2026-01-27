<?php
/**
 * WikiDocs - Collaborative Documentation Platform
 * Version 2.4.1
 * 
 * Protected by HTTP Basic Authentication
 * API tokens supported via access_token parameter
 */

$flag = getenv('FLAG') ?: 'FLAG{default_flag_for_testing}';

// Configuration
$BASIC_AUTH_ENABLED = true;
$BASIC_AUTH_USER = 'admin';
$BASIC_AUTH_PASS = 'x9K#mP2$vL7@nQ4w'; // Secure randomly generated password

// API Token database (simulated)
$valid_api_tokens = [
    'a1b2c3d4e5f6g7h8i9j0' => ['user' => 'api_user', 'scope' => 'read'],
    'z9y8x7w6v5u4t3s2r1q0' => ['user' => 'system', 'scope' => 'admin']
];

$authenticated = false;
$auth_method = null;

/**
 * Access Token Parser Middleware
 * Processes API tokens for programmatic access
 * 
 * VULNERABILITY: If access_token is present but invalid,
 * we call through without enforcing Basic Auth (fail-open)
 */
function processAccessToken($token, $valid_tokens) {
    global $authenticated, $auth_method;
    
    if ($token === null || !is_string($token)) {
        return false; // No token provided, continue to next auth method
    }
    
    // Check if token exists in our database
    if (isset($valid_tokens[$token])) {
        $authenticated = true;
        $auth_method = 'api_token';
        return true;
    }
    
    // VULNERABLE: Token was provided but invalid
    // Instead of rejecting, we just return and don't enforce Basic Auth
    // This mimics the CVE-2019-13337 behavior where invalid tokens bypass auth
    return true; // Indicates token processing happened (even if invalid)
}

/**
 * Basic Auth Handler
 */
function checkBasicAuth($expected_user, $expected_pass) {
    global $authenticated, $auth_method;
    
    if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW'])) {
        return false;
    }
    
    if ($_SERVER['PHP_AUTH_USER'] === $expected_user && 
        $_SERVER['PHP_AUTH_PW'] === $expected_pass) {
        $authenticated = true;
        $auth_method = 'basic_auth';
        return true;
    }
    
    return false;
}

// Check for access_token in query string or POST body
$access_token = isset($_GET['access_token']) ? $_GET['access_token'] : 
                (isset($_POST['access_token']) ? $_POST['access_token'] : null);

// Process access token first (vulnerable middleware)
$token_processed = processAccessToken($access_token, $valid_api_tokens);

// VULNERABILITY: If token was processed (even invalid), skip Basic Auth check
// This is the fail-open behavior from CVE-2019-13337
if (!$token_processed) {
    // Only check Basic Auth if no token was provided at all
    if ($BASIC_AUTH_ENABLED && !checkBasicAuth($BASIC_AUTH_USER, $BASIC_AUTH_PASS)) {
        header('WWW-Authenticate: Basic realm="WikiDocs Protected Area"');
        header('HTTP/1.0 401 Unauthorized');
        echo '<!DOCTYPE html>
<html>
<head><title>401 Unauthorized</title></head>
<body>
<h1>Authentication Required</h1>
<p>You must authenticate to access WikiDocs.</p>
<p><small>WikiDocs v2.4.1 - Powered by SecureAuth</small></p>
</body>
</html>';
        exit;
    }
}

// If we reach here, user is either authenticated or bypassed auth via token param
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiDocs - Documentation Platform</title>
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
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            font-size: 28px;
            font-weight: 300;
        }
        .header .version {
            font-size: 12px;
            opacity: 0.7;
        }
        .nav {
            background: #34495e;
            padding: 10px 40px;
        }
        .nav a {
            color: #ecf0f1;
            text-decoration: none;
            margin-right: 20px;
            font-size: 14px;
        }
        .nav a:hover {
            color: #3498db;
        }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .content-box {
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .content-box h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        .doc-list {
            list-style: none;
        }
        .doc-list li {
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }
        .doc-list li:last-child {
            border-bottom: none;
        }
        .doc-list a {
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }
        .doc-list a:hover {
            text-decoration: underline;
        }
        .doc-meta {
            color: #888;
            font-size: 12px;
            margin-top: 4px;
        }
        .sidebar {
            float: right;
            width: 280px;
            margin-left: 20px;
        }
        .main-content {
            overflow: hidden;
        }
        .alert {
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .alert-info {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .secret-docs {
            background: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 20px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .secret-docs h3 {
            color: #856404;
            margin-bottom: 10px;
        }
        .flag-display {
            background: #1a1a2e;
            color: #0f0;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: 12px;
        }
        .api-notice {
            background: #e7f3ff;
            border: 1px solid #b6d4fe;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            font-size: 13px;
        }
        .api-notice code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 WikiDocs</h1>
        <span class="version">v2.4.1 - Enterprise Documentation Platform</span>
    </div>
    
    <div class="nav">
        <a href="/">Home</a>
        <a href="/docs">Documentation</a>
        <a href="/api">API Reference</a>
        <a href="/admin">Admin Panel</a>
        <a href="/search">Search</a>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="content-box">
                <h2>Quick Links</h2>
                <ul class="doc-list">
                    <li><a href="#getting-started">Getting Started</a></li>
                    <li><a href="#installation">Installation Guide</a></li>
                    <li><a href="#configuration">Configuration</a></li>
                    <li><a href="#api-docs">API Documentation</a></li>
                    <li><a href="#troubleshooting">Troubleshooting</a></li>
                </ul>
            </div>
            
            <div class="content-box">
                <h2>System Status</h2>
                <p style="color: #28a745;">✓ All systems operational</p>
                <p class="doc-meta">Last checked: <?php echo date('Y-m-d H:i:s'); ?></p>
            </div>
        </div>
        
        <div class="main-content">
            <div class="alert alert-info">
                <strong>Welcome to WikiDocs!</strong> You have successfully accessed the protected documentation area.
                <?php if ($auth_method): ?>
                <br><small>Authenticated via: <?php echo htmlspecialchars($auth_method); ?></small>
                <?php endif; ?>
            </div>
            
            <div class="content-box">
                <h2>Documentation Index</h2>
                <ul class="doc-list">
                    <li>
                        <a href="/docs/overview">Platform Overview</a>
                        <div class="doc-meta">Introduction to WikiDocs features and capabilities</div>
                    </li>
                    <li>
                        <a href="/docs/installation">Installation Guide</a>
                        <div class="doc-meta">Step-by-step installation instructions</div>
                    </li>
                    <li>
                        <a href="/docs/authentication">Authentication Setup</a>
                        <div class="doc-meta">Configure Basic Auth, API tokens, and SSO</div>
                    </li>
                    <li>
                        <a href="/docs/api-reference">API Reference</a>
                        <div class="doc-meta">Complete REST API documentation</div>
                    </li>
                    <li>
                        <a href="/docs/plugins">Plugin Development</a>
                        <div class="doc-meta">Creating custom plugins and extensions</div>
                    </li>
                </ul>
                
                <div class="api-notice">
                    <strong>📌 API Access:</strong> For programmatic access, include your API token using the 
                    <code>access_token</code> parameter in your requests. 
                    Example: <code>GET /api/docs?access_token=YOUR_TOKEN</code>
                </div>
            </div>
            
            <div class="content-box secret-docs">
                <h3>🔒 Confidential: Internal Credentials</h3>
                <p>This section contains sensitive system information. Access is restricted to authenticated administrators.</p>
                <div class="flag-display">
                    SYSTEM_KEY: <?php echo htmlspecialchars($flag); ?>
                </div>
                <p class="doc-meta" style="margin-top: 10px;">
                    Last updated: <?php echo date('Y-m-d'); ?> | Classification: CONFIDENTIAL
                </p>
            </div>
        </div>
        
        <div style="clear: both;"></div>
    </div>
    
    <div class="footer">
        <p>WikiDocs v2.4.1 &copy; 2024 | <a href="/privacy">Privacy Policy</a> | <a href="/terms">Terms of Service</a></p>
        <p>Powered by SecureAuth Middleware</p>
    </div>
</body>
</html>

