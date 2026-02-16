<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($data['appName']) ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f6fa; color: #2d3436; }
        .navbar { background: #2d3436; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { color: #fff; font-size: 1.2rem; }
        .navbar nav a { color: #dfe6e9; text-decoration: none; margin-left: 1.5rem; font-size: 0.9rem; }
        .navbar nav a:hover { color: #74b9ff; }
        .container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: #fff; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { font-size: 1.1rem; margin-bottom: 0.8rem; color: #636e72; }
        .status-badge { display: inline-block; background: #00b894; color: #fff; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; }
        .info-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0; }
        .info-row:last-child { border-bottom: none; }
        .info-label { color: #636e72; }
        .footer { text-align: center; padding: 2rem; color: #b2bec3; font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1><?= htmlspecialchars($data['appName']) ?></h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/login">Login</a>
            <a href="/api/status">API Status</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>System Status</h2>
            <div class="info-row">
                <span class="info-label">Service Health</span>
                <span class="status-badge">Operational</span>
            </div>
            <div class="info-row">
                <span class="info-label">Your IP Address</span>
                <span><?= htmlspecialchars($data['clientIP']) ?></span>
            </div>
            <div class="info-row">
                <span class="info-label">Current Time (UTC)</span>
                <span><?= gmdate('Y-m-d H:i:s') ?></span>
            </div>
        </div>
        <div class="card">
            <h2>Quick Links</h2>
            <div class="info-row">
                <span class="info-label">Administration Panel</span>
                <span><a href="/panel">Access Panel</a> (internal network only)</span>
            </div>
            <div class="info-row">
                <span class="info-label">API Status</span>
                <span><a href="/api/status">View Status</a></span>
            </div>
        </div>
    </div>
    <div class="footer">
        &copy; <?= date('Y') ?> <?= htmlspecialchars($data['appName']) ?>. All rights reserved.
    </div>
</body>
</html>
