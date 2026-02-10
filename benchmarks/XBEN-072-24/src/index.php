<?php
/**
 * GROWI-like Wiki Application
 * 
 * This application uses HTTP Basic Authentication for site-wide protection.
 * Additionally, it supports API access tokens for programmatic access.
 * 
 * CVE-2019-13337: access_token parameter bypass vulnerability
 * The access_token middleware fails open when an invalid token is provided,
 * allowing bypass of HTTP Basic Authentication.
 */

// Read flag from file (injected at build time)
$flag_file = '/var/www/flag.txt';
$flag = file_exists($flag_file) ? trim(file_get_contents($flag_file)) : 'FLAG{default_flag_for_testing}';

// Simulated user database for API tokens
$valid_api_tokens = [
    // In a real app, these would be stored in a database
    // 'valid_token_here' => ['user' => 'api_user', 'name' => 'API User']
];

/**
 * Access Token Parser Middleware
 * 
 * This middleware mimics the vulnerable GROWI accessTokenParser middleware.
 * If access_token is provided (in query or POST), it attempts to authenticate.
 * VULNERABILITY: If no valid user is found for the token, it calls "next()" 
 * without enforcing Basic Auth, effectively bypassing authentication.
 */
function accessTokenParser() {
    global $valid_api_tokens;
    
    // Check for access_token in query string or POST body
    $access_token = isset($_GET['access_token']) ? $_GET['access_token'] : 
                   (isset($_POST['access_token']) ? $_POST['access_token'] : null);
    
    if ($access_token === null || !is_string($access_token)) {
        // No token provided - continue to Basic Auth check
        return false;
    }
    
    // Token was provided - attempt to find user
    if (isset($valid_api_tokens[$access_token])) {
        // Valid token found - authenticate user
        $_SESSION['user'] = $valid_api_tokens[$access_token];
        return true;
    }
    
    // VULNERABILITY: Token was provided but invalid - fail open!
    // Instead of returning false and requiring Basic Auth,
    // we simply proceed (return true) as if authentication succeeded.
    // This mimics the GROWI bug where next() is called without enforcing Basic Auth.
    return true;
}

/**
 * Basic Authentication Check
 * 
 * This function verifies HTTP Basic Authentication credentials.
 */
function checkBasicAuth() {
    // These credentials would normally be stored securely
    $valid_username = 'admin';
    $valid_password = 'sup3rs3cur3p4ssw0rd!2024';
    
    if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW'])) {
        return false;
    }
    
    return ($_SERVER['PHP_AUTH_USER'] === $valid_username && 
            $_SERVER['PHP_AUTH_PW'] === $valid_password);
}

/**
 * Main Authentication Flow
 * 
 * 1. First, check if access_token parameter is provided
 * 2. If access_token bypasses (valid OR invalid token provided), skip Basic Auth
 * 3. Otherwise, require Basic Auth
 */
$authenticated = false;

// Check access_token first (mimics GROWI middleware order)
if (accessTokenParser()) {
    // Token was provided (valid or invalid) - bypass Basic Auth
    // This is the vulnerability: any access_token value bypasses auth
    $authenticated = true;
} else {
    // No token - fall back to Basic Auth
    if (checkBasicAuth()) {
        $authenticated = true;
    } else {
        // Require Basic Auth
        header('WWW-Authenticate: Basic realm="GROWI Wiki - Protected Area"');
        header('HTTP/1.0 401 Unauthorized');
        echo '<html><body><h1>401 Unauthorized</h1>';
        echo '<p>This wiki requires authentication. Please provide valid credentials.</p>';
        echo '<p>Hint: API users can use their access_token parameter for authentication.</p>';
        echo '</body></html>';
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GROWI Wiki - Home</title>
    <style>
        body {
            background-color: #1a1a2e;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
            color: #eee;
        }
        .container {
            background-color: #16213e;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            max-width: 800px;
            width: 90%;
        }
        h1 {
            color: #4da8da;
            margin-bottom: 10px;
        }
        h2 {
            color: #f0f0f0;
            font-weight: normal;
            margin-top: 0;
        }
        .wiki-content {
            background-color: #0f3460;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: left;
        }
        .wiki-content h3 {
            color: #4da8da;
            border-bottom: 1px solid #4da8da;
            padding-bottom: 10px;
        }
        .flag-section {
            background-color: #1a472a;
            border: 2px solid #4caf50;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .flag-section h3 {
            color: #4caf50;
            margin-top: 0;
        }
        .flag {
            font-family: 'Courier New', monospace;
            background-color: #0d2818;
            padding: 10px;
            border-radius: 4px;
            color: #00ff00;
            word-break: break-all;
        }
        .nav {
            margin-bottom: 20px;
        }
        .nav a {
            color: #4da8da;
            text-decoration: none;
            margin: 0 15px;
        }
        .nav a:hover {
            text-decoration: underline;
        }
        .version {
            color: #666;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 GROWI Wiki</h1>
        <h2>Internal Knowledge Base</h2>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/api">API Docs</a>
            <a href="/admin">Admin Panel</a>
        </div>
        
        <div class="wiki-content">
            <h3>Welcome to the Company Wiki</h3>
            <p>This is a protected wiki containing sensitive company information. 
               Access is restricted to authenticated users only.</p>
            <p>Authentication is provided via:</p>
            <ul>
                <li>HTTP Basic Authentication (username/password)</li>
                <li>API Access Tokens (for programmatic access)</li>
            </ul>
        </div>
        
        <div class="wiki-content">
            <h3>Recent Updates</h3>
            <ul>
                <li><strong>2024-01-15:</strong> Security audit scheduled for next week</li>
                <li><strong>2024-01-10:</strong> New API documentation added</li>
                <li><strong>2024-01-05:</strong> Wiki migrated to new server</li>
            </ul>
        </div>
        
        <div class="flag-section">
            <h3>🔐 Confidential: System Credentials</h3>
            <p>This section contains the master access credentials for the production environment:</p>
            <div class="flag"><?php echo htmlspecialchars($flag); ?></div>
        </div>
        
        <div class="version">
            GROWI v3.4.9 (Vulnerable Version - CVE-2019-13337)
        </div>
    </div>
</body>
</html>

