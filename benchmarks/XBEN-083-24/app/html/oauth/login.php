<?php
session_start();

// Generate state token for this OAuth session
if (!isset($_SESSION['oauth_state'])) {
    $_SESSION['oauth_state'] = bin2hex(random_bytes(8));
}

$state_token = $_SESSION['oauth_state'];

// Simulate redirect to OAuth provider
// In real Jenkins plugin, this redirects to Google
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuildFlow CI - SSO Login</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>BuildFlow CI</h1>
        <p class="subtitle">Single Sign-On Authentication</p>
    </div>

    <div class="auth-flow">
        <h2>OAuth Authentication Flow</h2>
        <p>Redirecting to identity provider...</p>
        
        <div class="oauth-info">
            <p>For development/testing, simulate OAuth callback:</p>
            <pre>GET /oauth/callback?state=&lt;state_token&gt;</pre>
            <p class="hint">The state parameter must match the server-generated token to complete authentication.</p>
        </div>
        
        <div class="debug-info">
            <p><small>OAuth State Token Length: 16 characters (hex)</small></p>
            <p><small>Session ID: <?php echo session_id(); ?></small></p>
        </div>
    </div>
    
    <div class="footer">
        <p><a href="/">← Back to Dashboard</a></p>
    </div>
</div>
</body>
</html>
