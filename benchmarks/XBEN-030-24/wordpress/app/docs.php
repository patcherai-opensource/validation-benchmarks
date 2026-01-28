<?php
/**
 * ModuLink - Documentation
 */
session_start();
$is_logged_in = isset($_SESSION['user_id']);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation - ModuLink</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        header { background: #1e293b; padding: 15px 0; border-bottom: 1px solid #334155; }
        nav { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .logo { font-size: 1.5rem; font-weight: bold; color: #38bdf8; }
        .nav-links { display: flex; gap: 20px; }
        .nav-links a { color: #94a3b8; text-decoration: none; }
        .nav-links a:hover { color: #f8fafc; }
        h1 { margin: 30px 0 20px; }
        h2 { color: #38bdf8; margin: 25px 0 15px; }
        h3 { color: #94a3b8; margin: 20px 0 10px; }
        p { color: #94a3b8; line-height: 1.7; margin-bottom: 15px; }
        code { background: #334155; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #1e293b; padding: 15px; border-radius: 8px; overflow-x: auto; margin: 15px 0; border: 1px solid #334155; }
        pre code { background: none; padding: 0; }
        ul { color: #94a3b8; margin-left: 20px; margin-bottom: 15px; }
        li { margin-bottom: 8px; }
        .toc { background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #334155; }
        .toc a { color: #38bdf8; text-decoration: none; }
        .toc a:hover { text-decoration: underline; }
        footer { text-align: center; padding: 20px; color: #64748b; margin-top: 40px; }
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo">ModuLink</div>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/docs.php">Documentation</a>
                <a href="/api/status.php">API Status</a>
                <?php if ($is_logged_in): ?>
                    <a href="/dashboard.php">Dashboard</a>
                    <a href="/logout.php">Logout</a>
                <?php else: ?>
                    <a href="/login.php">Login</a>
                <?php endif; ?>
            </div>
        </nav>
    </header>

    <div class="container">
        <h1>ModuLink Documentation</h1>
        
        <div class="toc">
            <h3 style="margin-top: 0;">Table of Contents</h3>
            <ul style="list-style: none; margin-left: 0;">
                <li><a href="#getting-started">1. Getting Started</a></li>
                <li><a href="#authentication">2. Authentication</a></li>
                <li><a href="#plugins">3. Plugin Management</a></li>
                <li><a href="#api">4. API Reference</a></li>
                <li><a href="#troubleshooting">5. Troubleshooting</a></li>
            </ul>
        </div>

        <h2 id="getting-started">1. Getting Started</h2>
        <p>ModuLink is an enterprise plugin management system designed to help you manage application extensions from various sources including Git repositories, npm packages, and our marketplace.</p>
        
        <h3>System Requirements</h3>
        <ul>
            <li>PHP 8.0 or higher</li>
            <li>Git 2.x installed on the server</li>
            <li>Node.js 18+ (for npm plugins)</li>
            <li>Minimum 2GB RAM</li>
        </ul>

        <h2 id="authentication">2. Authentication</h2>
        <p>ModuLink supports multiple user roles with different permission levels:</p>
        <ul>
            <li><strong>Admin</strong> - Full access to all features including plugin installation</li>
            <li><strong>Developer</strong> - Can view and configure plugins</li>
            <li><strong>Viewer</strong> - Read-only access to dashboards</li>
        </ul>

        <h2 id="plugins">3. Plugin Management</h2>
        <p>Administrators can install plugins from three sources:</p>
        
        <h3>From Git Repository</h3>
        <p>To install a plugin from Git, provide the repository URL and a unique plugin name. The system will clone the repository into the plugins directory.</p>
        <pre><code>POST /admin/plugins.php
Content-Type: application/x-www-form-urlencoded

action=install_git&plugin_name=my-plugin&git_url=https://github.com/user/repo.git</code></pre>

        <h3>From NPM</h3>
        <p>NPM plugins can be installed by specifying the package name:</p>
        <pre><code>POST /admin/plugins.php
Content-Type: application/x-www-form-urlencoded

action=install_npm&package_name=@scope/package-name</code></pre>

        <h2 id="api">4. API Reference</h2>
        <p>ModuLink provides a REST API for programmatic access. See the <a href="/api/status.php" style="color: #38bdf8;">API Status</a> page for available endpoints.</p>
        
        <h3>Available Endpoints</h3>
        <ul>
            <li><code>GET /api/status.php</code> - System status</li>
            <li><code>GET /api/plugins/list</code> - List installed plugins</li>
            <li><code>GET /api/health</code> - Health check endpoint</li>
        </ul>

        <h2 id="troubleshooting">5. Troubleshooting</h2>
        <h3>Plugin Installation Fails</h3>
        <p>If plugin installation fails, check the following:</p>
        <ul>
            <li>Ensure Git is installed and accessible</li>
            <li>Verify the repository URL is correct and accessible</li>
            <li>Check that the plugins directory is writable</li>
            <li>Review the installation logs in <code>/logs/plugin_install.log</code></li>
        </ul>
    </div>

    <footer>
        <p>&copy; 2024 ModuLink v3.2.1. All rights reserved.</p>
    </footer>
</body>
</html>
