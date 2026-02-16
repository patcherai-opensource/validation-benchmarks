<?php
session_start();
require_once __DIR__ . '/includes/config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VaultPass - Collaborative Password Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6fa; color: #2c3e50; }
        .header { background: #2c3e50; color: white; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 22px; font-weight: 600; }
        .header .version { font-size: 12px; opacity: 0.7; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 20px; }
        .login-card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 40px; max-width: 420px; margin: 60px auto; }
        .login-card h2 { margin-bottom: 24px; font-size: 20px; color: #2c3e50; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 6px; font-size: 14px; font-weight: 500; color: #555; }
        .form-group input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .form-group input:focus { border-color: #3498db; outline: none; box-shadow: 0 0 0 2px rgba(52,152,219,0.2); }
        .btn { display: inline-block; padding: 10px 24px; background: #3498db; color: white; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; width: 100%; }
        .btn:hover { background: #2980b9; }
        .alert { padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
        .alert-error { background: #fce4e4; color: #c0392b; border: 1px solid #e6b0aa; }
        .alert-success { background: #e8f8f5; color: #1e8449; border: 1px solid #a9dfbf; }
        .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; margin-top: 40px; }
        .api-notice { background: #eaf2f8; border: 1px solid #aed6f1; border-radius: 4px; padding: 16px; margin-top: 24px; font-size: 13px; color: #2471a3; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>VaultPass</h1>
            <span class="version">Collaborative Password Manager</span>
        </div>
    </div>
    <div class="container">
        <div class="login-card">
            <h2>Sign In</h2>
            <?php if (isset($_GET['error'])): ?>
                <div class="alert alert-error">Invalid credentials. Please try again.</div>
            <?php endif; ?>
            <?php if (isset($_GET['logout'])): ?>
                <div class="alert alert-success">You have been logged out successfully.</div>
            <?php endif; ?>
            <form action="/login.php" method="POST">
                <div class="form-group">
                    <label for="login">Username</label>
                    <input type="text" id="login" name="login" placeholder="Enter your username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                <button type="submit" class="btn">Sign In</button>
            </form>
            <div class="api-notice">
                API access is available for integrations. Refer to the documentation for endpoint details.
            </div>
        </div>
    </div>
    <div class="footer">
        &copy; 2023 VaultPass. All rights reserved.
    </div>
</body>
</html>
