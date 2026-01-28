<?php
// Help page (not vulnerable, just informational)
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Help - SecureAuth Portal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            width: 100%;
            max-width: 650px;
        }
        h1 {
            color: #1a1a2e;
            font-size: 28px;
            margin-bottom: 20px;
        }
        h2 {
            color: #0f3460;
            font-size: 20px;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        p {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        ul {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        li {
            color: #666;
            margin-bottom: 8px;
        }
        .nav-links {
            text-align: center;
            margin-top: 30px;
        }
        .nav-links a {
            color: #0f3460;
            text-decoration: none;
            font-size: 14px;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 SecureAuth Portal Help</h1>
        
        <h2>Getting Started</h2>
        <p>SecureAuth Portal uses two-factor authentication (2FA) to protect your account.</p>
        
        <h2>How to Sign In</h2>
        <ul>
            <li>Enter your username and password</li>
            <li>Optionally check "Remember me" to stay signed in on this device</li>
            <li>Click "Sign In"</li>
            <li>Enter the 6-digit code from your authenticator app</li>
            <li>Click "Verify" to complete sign-in</li>
        </ul>
        
        <h2>Remember Me Feature</h2>
        <p>The "Remember me" feature allows you to stay signed in on trusted devices for up to 30 days. When enabled, you'll receive a secure cookie that automatically authenticates your device.</p>
        
        <h2>Supported Authenticator Apps</h2>
        <ul>
            <li>Google Authenticator</li>
            <li>Microsoft Authenticator</li>
            <li>Authy</li>
            <li>Any TOTP-compatible app</li>
        </ul>
        
        <h2>Troubleshooting</h2>
        <p>If you're having issues:</p>
        <ul>
            <li>Ensure your system time is synchronized</li>
            <li>Try clearing your browser cookies</li>
            <li>Contact your administrator if problems persist</li>
        </ul>
        
        <h2>Security Information</h2>
        <p>Version: <code>SecureAuth Portal v3.25.0</code></p>
        <p>This system implements industry-standard two-factor authentication protocols.</p>
        
        <div class="nav-links">
            <a href="/">← Back to Sign In</a>
        </div>
    </div>
</body>
</html>
