<?php
/**
 * EzContent CMS - Setup Configuration
 * Displays system configuration status
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EzContent CMS - Setup</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 40px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a1a2e;
            border-bottom: 2px solid #0f3460;
            padding-bottom: 10px;
        }
        .config-section {
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }
        .config-section h3 {
            color: #0f3460;
            margin-bottom: 10px;
        }
        .config-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .config-item:last-child {
            border-bottom: none;
        }
        .config-key {
            font-weight: 500;
        }
        .config-value {
            color: #666;
            font-family: monospace;
        }
        .status-ok {
            color: #2e7d32;
        }
        .status-warn {
            color: #f57c00;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #0f3460;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>EzContent CMS Setup</h1>
        
        <div class="config-section">
            <h3>Site Configuration (site.ini)</h3>
            <div class="config-item">
                <span class="config-key">SiteName</span>
                <span class="config-value">EzContent Administration</span>
            </div>
            <div class="config-item">
                <span class="config-key">SiteURL</span>
                <span class="config-value">localhost</span>
            </div>
            <div class="config-item">
                <span class="config-key">DefaultAccess</span>
                <span class="config-value">admin</span>
            </div>
        </div>
        
        <div class="config-section">
            <h3>Login Handler Configuration</h3>
            <div class="config-item">
                <span class="config-key">LoginHandler[]</span>
                <span class="config-value">standard</span>
            </div>
            <div class="config-item">
                <span class="config-key">LoginHandler[]</span>
                <span class="config-value">LDAP</span>
            </div>
            <div class="config-item">
                <span class="config-key">LDAPServer</span>
                <span class="config-value">ldap.ezcontent.local</span>
            </div>
            <div class="config-item">
                <span class="config-key">LDAPPort</span>
                <span class="config-value">389</span>
            </div>
            <div class="config-item">
                <span class="config-key">TextFileEnabled</span>
                <span class="config-value">false</span>
            </div>
        </div>
        
        <div class="config-section">
            <h3>User Database Status</h3>
            <div class="config-item">
                <span class="config-key">Total Users</span>
                <span class="config-value">3</span>
            </div>
            <div class="config-item">
                <span class="config-key">Administrator Accounts</span>
                <span class="config-value">1</span>
            </div>
            <div class="config-item">
                <span class="config-key">External Auth Users (LDAP)</span>
                <span class="config-value class="status-warn">1 (password_hash_type=0)</span>
            </div>
        </div>
        
        <div class="config-section">
            <h3>System Status</h3>
            <div class="config-item">
                <span class="config-key">PHP Version</span>
                <span class="config-value status-ok"><?php echo phpversion(); ?></span>
            </div>
            <div class="config-item">
                <span class="config-key">Database Connection</span>
                <span class="config-value status-ok">OK</span>
            </div>
            <div class="config-item">
                <span class="config-key">LDAP Extension</span>
                <span class="config-value status-warn">Not Available</span>
            </div>
        </div>
        
        <a href="/" class="back-link">&larr; Back to Login</a>
    </div>
</body>
</html>
