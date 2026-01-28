<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
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
    <title>API Documentation - GeoRedirect Pro</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="service-header">
        <h1>GeoRedirect Pro</h1>
        <p class="tagline">API Documentation</p>
    </header>

    <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/lookup.php">IP Lookup</a>
        <a href="/docs.php" class="active">API Documentation</a>
        <a href="/status.php">Service Status</a>
    </nav>

    <section class="docs-section">
        <h2>REST API Reference</h2>
        <p>API Version: <?php echo htmlspecialchars($config['api_version'] ?? '2.0'); ?></p>
        
        <article class="endpoint-doc">
            <h3>GET /lookup.php</h3>
            <p>Lookup geolocation information for an IP address.</p>
            
            <h4>Parameters</h4>
            <table class="params-table">
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Required</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td><code>ip</code></td>
                    <td>string</td>
                    <td>Yes</td>
                    <td>IPv4 address to lookup (e.g., 8.8.8.8)</td>
                </tr>
            </table>
            
            <h4>Example Request</h4>
            <pre class="code-block">GET /lookup.php?ip=8.8.8.8</pre>
            
            <h4>Response</h4>
            <p>Returns HTML page with lookup results including country code, country name, and region.</p>
        </article>

        <article class="endpoint-doc">
            <h3>GET /api/redirect.php</h3>
            <p>Programmatic endpoint for redirect resolution.</p>
            
            <h4>Parameters</h4>
            <table class="params-table">
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Required</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td><code>ipAddress</code></td>
                    <td>string</td>
                    <td>Yes</td>
                    <td>Client IP address for redirect lookup</td>
                </tr>
                <tr>
                    <td><code>format</code></td>
                    <td>string</td>
                    <td>No</td>
                    <td>Response format: json (default), xml</td>
                </tr>
            </table>
        </article>

        <article class="endpoint-doc">
            <h3>GET /status.php</h3>
            <p>Returns service health status and metrics.</p>
        </article>
    </section>

    <section class="rate-limits">
        <h3>Rate Limiting</h3>
        <p>Maximum requests: <?php echo htmlspecialchars($config['max_requests_per_minute'] ?? '100'); ?> per minute per IP address.</p>
        <p>Exceeded limits return HTTP 429 status code.</p>
    </section>

    <section class="error-codes">
        <h3>Error Codes</h3>
        <table class="data-table">
            <tr>
                <th>Code</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>200</td>
                <td>Success</td>
            </tr>
            <tr>
                <td>400</td>
                <td>Invalid IP address format</td>
            </tr>
            <tr>
                <td>404</td>
                <td>IP not found in database</td>
            </tr>
            <tr>
                <td>429</td>
                <td>Rate limit exceeded</td>
            </tr>
            <tr>
                <td>500</td>
                <td>Internal server error</td>
            </tr>
        </table>
    </section>

    <footer class="main-footer">
        <p>&copy; 2024 GeoRedirect Pro. All rights reserved.</p>
    </footer>
</div>
</body>
</html>
<?php $conn->close(); ?>
