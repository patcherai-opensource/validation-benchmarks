<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    $db_status = $conn->connect_error ? 'Error' : 'Connected';
    
    $stats = [];
    if (!$conn->connect_error) {
        $ip_count = $conn->query("SELECT COUNT(*) as cnt FROM ip_country_mapping")->fetch_assoc()['cnt'];
        $lang_count = $conn->query("SELECT COUNT(*) as cnt FROM language_preferences WHERE is_active = 1")->fetch_assoc()['cnt'];
        $log_count = $conn->query("SELECT COUNT(*) as cnt FROM redirect_logs")->fetch_assoc()['cnt'];
        $stats = [
            'ip_ranges' => $ip_count,
            'languages' => $lang_count,
            'total_lookups' => $log_count
        ];
        
        $config_result = $conn->query("SELECT config_key, config_value FROM system_config WHERE is_public = 1");
        $config = [];
        while ($row = $config_result->fetch_assoc()) {
            $config[$row['config_key']] = $row['config_value'];
        }
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Service Status - GeoRedirect Pro</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="service-header">
        <h1>GeoRedirect Pro</h1>
        <p class="tagline">Service Status</p>
    </header>

    <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/lookup.php">IP Lookup</a>
        <a href="/docs.php">API Documentation</a>
        <a href="/status.php" class="active">Service Status</a>
    </nav>

    <section class="status-section">
        <h2>System Health</h2>
        
        <div class="status-grid">
            <div class="status-card <?php echo $db_status === 'Connected' ? 'status-ok' : 'status-error'; ?>">
                <h3>Database</h3>
                <p class="status-value"><?php echo $db_status; ?></p>
            </div>
            
            <div class="status-card status-ok">
                <h3>Web Server</h3>
                <p class="status-value">Running</p>
            </div>
            
            <div class="status-card status-ok">
                <h3>Cache</h3>
                <p class="status-value">Active (TTL: <?php echo $config['cache_ttl_seconds'] ?? '3600'; ?>s)</p>
            </div>
        </div>
    </section>

    <section class="metrics-section">
        <h2>Service Metrics</h2>
        <table class="data-table">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>IP Ranges in Database</td>
                <td><?php echo htmlspecialchars($stats['ip_ranges'] ?? 'N/A'); ?></td>
            </tr>
            <tr>
                <td>Active Language Mappings</td>
                <td><?php echo htmlspecialchars($stats['languages'] ?? 'N/A'); ?></td>
            </tr>
            <tr>
                <td>Total Lookups (logged)</td>
                <td><?php echo htmlspecialchars($stats['total_lookups'] ?? 'N/A'); ?></td>
            </tr>
            <tr>
                <td>API Version</td>
                <td><?php echo htmlspecialchars($config['api_version'] ?? 'N/A'); ?></td>
            </tr>
            <tr>
                <td>Rate Limit</td>
                <td><?php echo htmlspecialchars($config['max_requests_per_minute'] ?? 'N/A'); ?> req/min</td>
            </tr>
        </table>
    </section>

    <section class="recent-activity">
        <h2>Recent Lookups</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>IP Address</th>
                    <th>Country</th>
                    <th>Redirect</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
            <?php
            if (!$conn->connect_error) {
                $logs = $conn->query("SELECT * FROM redirect_logs ORDER BY logged_at DESC LIMIT 10");
                while ($log = $logs->fetch_assoc()) {
                    echo "<tr>
                            <td>" . htmlspecialchars($log['ip_address']) . "</td>
                            <td>" . htmlspecialchars($log['detected_country']) . "</td>
                            <td>" . htmlspecialchars($log['redirect_target']) . "</td>
                            <td>" . htmlspecialchars($log['logged_at']) . "</td>
                          </tr>";
                }
            }
            ?>
            </tbody>
        </table>
    </section>

    <footer class="main-footer">
        <p>&copy; 2024 GeoRedirect Pro. All rights reserved.</p>
    </footer>
</div>
</body>
</html>
<?php if (!$conn->connect_error) $conn->close(); ?>
