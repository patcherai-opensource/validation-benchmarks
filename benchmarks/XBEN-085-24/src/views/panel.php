<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - <?= htmlspecialchars($data['appName']) ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f6fa; color: #2d3436; }
        .navbar { background: #2d3436; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { color: #fff; font-size: 1.2rem; }
        .navbar .badge { background: #d63031; color: #fff; padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.7rem; margin-left: 0.5rem; vertical-align: middle; }
        .navbar nav a { color: #dfe6e9; text-decoration: none; margin-left: 1.5rem; font-size: 0.9rem; }
        .container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: #fff; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { font-size: 1.1rem; margin-bottom: 0.8rem; color: #636e72; }
        .info-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0; }
        .info-row:last-child { border-bottom: none; }
        .info-label { color: #636e72; }
        .info-value { font-family: monospace; font-size: 0.9rem; }
        .secret-value { background: #ffeaa7; padding: 0.2rem 0.5rem; border-radius: 3px; font-family: monospace; word-break: break-all; }
        .footer { text-align: center; padding: 2rem; color: #b2bec3; font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1><?= htmlspecialchars($data['appName']) ?> <span class="badge">ADMIN</span></h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/panel">Panel</a>
            <a href="/panel/diagnostics">Diagnostics</a>
            <a href="/logout">Logout</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>System Overview</h2>
            <div class="info-row">
                <span class="info-label">Server Time</span>
                <span class="info-value"><?= htmlspecialchars($data['serverTime']) ?></span>
            </div>
            <div class="info-row">
                <span class="info-label">PHP Version</span>
                <span class="info-value"><?= htmlspecialchars($data['phpVersion']) ?></span>
            </div>
            <div class="info-row">
                <span class="info-label">System Load</span>
                <span class="info-value"><?= implode(', ', array_map(function($v) { return number_format($v, 2); }, $data['systemLoad'])) ?></span>
            </div>
            <div class="info-row">
                <span class="info-label">Memory Usage</span>
                <span class="info-value"><?= $data['memoryUsage'] ?> MB</span>
            </div>
            <div class="info-row">
                <span class="info-label">Disk Free</span>
                <span class="info-value"><?= $data['diskFree'] ?> GB</span>
            </div>
        </div>
        <div class="card">
            <h2>Network Information</h2>
            <div class="info-row">
                <span class="info-label">Your IP Address</span>
                <span class="info-value"><?= htmlspecialchars($data['clientIP']) ?></span>
            </div>
        </div>
        <div class="card">
            <h2>System Credentials</h2>
            <div class="info-row">
                <span class="info-label">API Secret Token</span>
                <span class="secret-value"><?= htmlspecialchars($data['secretToken']) ?></span>
            </div>
        </div>
    </div>
    <div class="footer">
        &copy; <?= date('Y') ?> <?= htmlspecialchars($data['appName']) ?>. Internal use only.
    </div>
</body>
</html>
