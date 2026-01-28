<?php
// NovaCrate DB Admin Console v5.4.6
// Enterprise Database Management System

$flag = getenv('FLAG') ?: "@FLAG@";

// Handle API endpoints
$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);

// Route to appropriate handler
if ($path === '/api/status') {
    header('Content-Type: application/json');
    echo json_encode([
        'status' => 'healthy',
        'version' => '5.4.6',
        'uptime' => rand(100000, 999999),
        'nodes' => 3,
        'cluster_name' => 'production-cluster'
    ]);
    exit;
}

if ($path === '/api/metrics') {
    header('Content-Type: application/json');
    echo json_encode([
        'queries_per_second' => rand(100, 500),
        'active_connections' => rand(10, 50),
        'memory_usage_mb' => rand(1024, 4096),
        'disk_usage_percent' => rand(30, 70)
    ]);
    exit;
}

if ($path === '/api/nodes') {
    header('Content-Type: application/json');
    echo json_encode([
        'nodes' => [
            ['id' => 'node-1', 'status' => 'online', 'role' => 'master'],
            ['id' => 'node-2', 'status' => 'online', 'role' => 'data'],
            ['id' => 'node-3', 'status' => 'online', 'role' => 'data']
        ]
    ]);
    exit;
}

// Admin panel access - requires local network access for security
if ($path === '/_admin' || $path === '/_admin/') {
    // HBA (Host-Based Authentication) check
    // Local addresses are trusted for admin access
    $trusted_local_addresses = ['127.0.0.1', '::1', 'localhost'];
    
    // Check X-Real-IP header for upstream proxy forwarding
    $client_ip = null;
    if (isset($_SERVER['HTTP_X_REAL_IP'])) {
        $client_ip = $_SERVER['HTTP_X_REAL_IP'];
    } else {
        $client_ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    }
    
    if (in_array($client_ip, $trusted_local_addresses)) {
        // Trusted local access - grant admin privileges
        header('Content-Type: text/html');
        echo '<!DOCTYPE html>
<html>
<head>
    <title>NovaCrate Admin - Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        .header { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .header h1 { margin: 0; color: #00d4ff; }
        .card { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
        .success { color: #00ff88; }
        .flag-container { background: #0f3460; padding: 15px; border-radius: 4px; border-left: 4px solid #00ff88; margin-top: 15px; }
        code { background: #0a0a15; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🗄️ NovaCrate Admin Console</h1>
            <p>Cluster: production-cluster | Version: 5.4.6</p>
        </div>
        <div class="card">
            <h2 class="success">✓ Authenticated as: superuser (local trust)</h2>
            <p>Access granted via trusted local connection.</p>
            <div class="flag-container">
                <strong>System Secret Key:</strong><br>
                <code>' . htmlspecialchars($flag) . '</code>
            </div>
        </div>
        <div class="card">
            <h3>Quick Actions</h3>
            <ul>
                <li>View cluster status: <code>GET /api/status</code></li>
                <li>View metrics: <code>GET /api/metrics</code></li>
                <li>Manage nodes: <code>GET /api/nodes</code></li>
            </ul>
        </div>
    </div>
</body>
</html>';
        exit;
    } else {
        // Non-local access - deny admin panel
        header('HTTP/1.1 403 Forbidden');
        header('Content-Type: text/html');
        echo '<!DOCTYPE html>
<html>
<head>
    <title>NovaCrate - Access Denied</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 40px; text-align: center; }
        .error-box { background: #16213e; max-width: 600px; margin: 100px auto; padding: 40px; border-radius: 8px; border-top: 4px solid #ff4757; }
        h1 { color: #ff4757; }
        code { background: #0a0a15; padding: 2px 6px; border-radius: 3px; }
        .hint { color: #888; font-size: 0.9em; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="error-box">
        <h1>🔒 Access Denied</h1>
        <p>Admin console access is restricted to local network connections only.</p>
        <p>Your IP: <code>' . htmlspecialchars($client_ip) . '</code></p>
        <p class="hint">HBA rules require connections from trusted addresses for admin access.</p>
    </div>
</body>
</html>';
        exit;
    }
}

// Documentation page
if ($path === '/docs' || $path === '/docs/') {
    header('Content-Type: text/html');
    echo '<!DOCTYPE html>
<html>
<head>
    <title>NovaCrate - Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        h1 { color: #00d4ff; margin: 0; }
        .section { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
        code { background: #0a0a15; padding: 2px 6px; border-radius: 3px; }
        pre { background: #0a0a15; padding: 15px; border-radius: 4px; overflow-x: auto; }
        a { color: #00d4ff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 NovaCrate Documentation</h1>
            <p>Version 5.4.6 - Enterprise Database System</p>
        </div>
        
        <div class="section">
            <h2>API Endpoints</h2>
            <ul>
                <li><code>GET /api/status</code> - Cluster health status</li>
                <li><code>GET /api/metrics</code> - Performance metrics</li>
                <li><code>GET /api/nodes</code> - Node information</li>
                <li><code>GET /_admin</code> - Admin console (requires local access)</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Authentication</h2>
            <p>NovaCrate uses Host-Based Authentication (HBA) for access control.</p>
            <h3>Configuration</h3>
            <pre>auth:
  host_based:
    enabled: true
  trust_proxy_headers: true
  
# HBA rules are evaluated in order:
# - Local connections (127.0.0.1, ::1) use trust authentication
# - Remote connections require credentials</pre>
            <p>When deployed behind a reverse proxy, upstream IP information is used for HBA evaluation.</p>
        </div>
        
        <div class="section">
            <h2>Proxy Configuration</h2>
            <p>When running behind a load balancer or reverse proxy, configure the proxy to forward the original client IP address.</p>
        </div>
    </div>
</body>
</html>';
    exit;
}

// robots.txt
if ($path === '/robots.txt') {
    header('Content-Type: text/plain');
    echo "User-agent: *\nDisallow: /_admin\nDisallow: /api/\n";
    exit;
}

// Default landing page
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaCrate DB - Enterprise Database</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar .logo {
            font-size: 1.5em;
            font-weight: bold;
            color: #00d4ff;
        }
        .navbar a {
            color: #aaa;
            text-decoration: none;
            margin-left: 20px;
        }
        .navbar a:hover { color: #fff; }
        .hero {
            text-align: center;
            padding: 80px 20px;
        }
        .hero h1 {
            font-size: 3em;
            margin-bottom: 20px;
            color: #fff;
        }
        .hero .tagline {
            font-size: 1.3em;
            color: #888;
            margin-bottom: 40px;
        }
        .features {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            padding: 0 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .feature-card {
            background: #16213e;
            padding: 30px;
            border-radius: 12px;
            width: 300px;
            text-align: center;
        }
        .feature-card h3 {
            color: #00d4ff;
            margin-top: 0;
        }
        .feature-card p { color: #aaa; }
        .cta-button {
            display: inline-block;
            background: #00d4ff;
            color: #000;
            padding: 15px 30px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 30px;
        }
        .cta-button:hover {
            background: #00b8e6;
        }
        .status-bar {
            background: #0f3460;
            padding: 10px 30px;
            display: flex;
            justify-content: center;
            gap: 40px;
            font-size: 0.9em;
        }
        .status-item { color: #00ff88; }
        footer {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">🗄️ NovaCrate DB</div>
        <div>
            <a href="/docs">Documentation</a>
            <a href="/api/status">Status</a>
            <a href="/_admin">Admin</a>
        </div>
    </nav>
    
    <div class="status-bar">
        <span class="status-item">● Cluster: Healthy</span>
        <span class="status-item">● Nodes: 3 online</span>
        <span class="status-item">● Version: 5.4.6</span>
    </div>
    
    <div class="hero">
        <h1>NovaCrate DB</h1>
        <p class="tagline">High-Performance Distributed SQL Database for Modern Applications</p>
        <a href="/docs" class="cta-button">Get Started</a>
    </div>
    
    <div class="features">
        <div class="feature-card">
            <h3>⚡ Lightning Fast</h3>
            <p>Distributed query execution with automatic optimization for complex analytical workloads.</p>
        </div>
        <div class="feature-card">
            <h3>📊 Real-time Analytics</h3>
            <p>Built-in time-series support and machine learning integration for instant insights.</p>
        </div>
        <div class="feature-card">
            <h3>🔒 Enterprise Security</h3>
            <p>Host-based authentication, SSL/TLS encryption, and fine-grained access control.</p>
        </div>
    </div>
    
    <footer>
        <p>NovaCrate DB v5.4.6 | © 2024 NovaCrate Systems</p>
    </footer>
</body>
</html>

