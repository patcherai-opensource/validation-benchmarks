<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    // Load service config
    $config_result = $conn->query("SELECT config_key, config_value FROM system_config WHERE is_public = 1");
    $config = [];
    while ($row = $config_result->fetch_assoc()) {
        $config[$row['config_key']] = $row['config_value'];
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($config['service_name'] ?? 'GeoRedirect'); ?> - IP Geolocation &amp; Language Redirect</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="service-header">
        <h1><?php echo htmlspecialchars($config['service_name'] ?? 'GeoRedirect'); ?></h1>
        <p class="tagline">Intelligent IP-based Language Redirection Service</p>
        <p class="version">API Version: <?php echo htmlspecialchars($config['api_version'] ?? '2.0'); ?></p>
    </header>

    <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/lookup.php">IP Lookup</a>
        <a href="/docs.php">API Documentation</a>
        <a href="/status.php">Service Status</a>
    </nav>

    <section class="hero">
        <h2>Welcome to GeoRedirect Pro</h2>
        <p>Our service provides real-time IP geolocation to automatically redirect users to region-specific content. Perfect for multilingual websites and global applications.</p>
    </section>

    <section class="features">
        <h3>Key Features</h3>
        <ul>
            <li>Real-time IP to country code resolution</li>
            <li>Automatic language preference detection</li>
            <li>Low-latency redirect rules engine</li>
            <li>Comprehensive logging and analytics</li>
            <li>REST API for integration</li>
        </ul>
    </section>

    <section class="supported-regions">
        <h3>Supported Regions</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Country</th>
                    <th>Code</th>
                    <th>Language</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
            <?php
            $lang_result = $conn->query("SELECT lp.country_code, lp.preferred_language, lp.is_active, icm.country_name 
                                         FROM language_preferences lp 
                                         LEFT JOIN ip_country_mapping icm ON lp.country_code = icm.country_code 
                                         GROUP BY lp.country_code 
                                         ORDER BY lp.country_code");
            if ($lang_result && $lang_result->num_rows > 0) {
                while($row = $lang_result->fetch_assoc()) {
                    $status = $row['is_active'] ? 'Active' : 'Disabled';
                    $status_class = $row['is_active'] ? 'status-active' : 'status-disabled';
                    echo "<tr>
                            <td>" . htmlspecialchars($row['country_name'] ?? 'Unknown') . "</td>
                            <td>" . htmlspecialchars($row['country_code']) . "</td>
                            <td>" . htmlspecialchars($row['preferred_language']) . "</td>
                            <td class='{$status_class}'>{$status}</td>
                          </tr>";
                }
            }
            ?>
            </tbody>
        </table>
    </section>

    <section class="quick-test">
        <h3>Quick Lookup</h3>
        <p>Test an IP address to see geolocation results:</p>
        <form action="lookup.php" method="GET" class="lookup-form">
            <input type="text" name="ip" placeholder="Enter IP address (e.g., 8.8.8.8)" />
            <button type="submit">Lookup</button>
        </form>
    </section>

    <footer class="main-footer">
        <p>&copy; 2024 GeoRedirect Pro. All rights reserved.</p>
        <p>For API access, see our <a href="/docs.php">documentation</a>.</p>
    </footer>
</div>
</body>
</html>
<?php $conn->close(); ?>
