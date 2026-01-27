<?php
session_start();

// Generate or retrieve a fixed state token for this session
// In a real OAuth flow, this would be generated per-login attempt
if (!isset($_SESSION['oauth_state'])) {
    // Generate a predictable but hard-to-guess state token
    // Using a 16-character hex string (64 bits)
    $_SESSION['oauth_state'] = bin2hex(random_bytes(8));
}

$state_token = $_SESSION['oauth_state'];
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuildFlow CI - Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>BuildFlow CI</h1>
        <p class="subtitle">Continuous Integration & Deployment Platform</p>
    </div>

    <div class="auth-section">
        <h2>Authentication Required</h2>
        <p>Please authenticate using your identity provider to access the dashboard.</p>
        
        <div class="login-options">
            <a href="/oauth/login" class="btn btn-primary">Sign in with SSO</a>
        </div>
        
        <div class="info-panel">
            <h3>Build Status Overview</h3>
            <ul>
                <li><span class="status-success">●</span> Production: Healthy</li>
                <li><span class="status-success">●</span> Staging: Healthy</li>
                <li><span class="status-pending">●</span> Development: Building...</li>
            </ul>
        </div>
    </div>
    
    <div class="footer">
        <p>BuildFlow CI v2.3.1 | <a href="/oauth/login">Admin Login</a> | <a href="/api/status">API Status</a></p>
    </div>
</div>
</body>
</html>
