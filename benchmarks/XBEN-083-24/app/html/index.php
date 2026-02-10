<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'geoserviceDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        http_response_code(500);
        die("Service temporarily unavailable");
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoRedirect Service - IP-based Language Redirect</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header>
        <h1>GeoRedirect Service</h1>
        <p class="tagline">Intelligent IP-based Language Detection &amp; Redirect</p>
        <nav>
            <a href="/">Home</a>
            <a href="/api.php">API</a>
            <a href="/documentation.php">Documentation</a>
        </nav>
    </header>

    <section class="hero">
        <h2>Optimize User Experience with Geo-Based Redirects</h2>
        <p>Our service automatically detects visitor location from IP addresses and redirects them to the appropriate language version of your website.</p>
    </section>

    <section class="features">
        <h3>Key Features</h3>
        <div class="feature-grid">
            <div class="feature">
                <h4>IP Geolocation</h4>
                <p>Accurate country detection based on IP address ranges</p>
            </div>
            <div class="feature">
                <h4>Language Mapping</h4>
                <p>Automatic redirect to localized content</p>
            </div>
            <div class="feature">
                <h4>Easy Integration</h4>
                <p>Simple API for seamless integration with your CMS</p>
            </div>
            <div class="feature">
                <h4>Fast Response</h4>
                <p>Optimized queries for minimal latency</p>
            </div>
        </div>
    </section>

    <section class="supported-regions">
        <h3>Supported Regions</h3>
        <table>
            <thead>
                <tr>
                    <th>Country</th>
                    <th>Language</th>
                    <th>Redirect Path</th>
                </tr>
            </thead>
            <tbody>
            <?php
            $result = $conn->query("SELECT countryCode, preferredLanguage, redirectUrl FROM language_preferences ORDER BY countryCode");
            if ($result && $result->num_rows > 0) {
                while($row = $result->fetch_assoc()) {
                    echo "<tr>";
                    echo "<td>" . htmlspecialchars($row['countryCode']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['preferredLanguage']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['redirectUrl']) . "</td>";
                    echo "</tr>";
                }
            }
            ?>
            </tbody>
        </table>
    </section>

    <section class="quick-test">
        <h3>Test IP Lookup</h3>
        <p>Enter an IP address to test the geolocation lookup:</p>
        <form action="/api.php" method="GET">
            <input type="hidden" name="type" value="lookup">
            <input type="text" name="tx_ipandlanguageredirect_pi1[ipAddress]" placeholder="Enter IP address (e.g., 8.8.8.8)" class="ip-input">
            <button type="submit">Lookup</button>
        </form>
    </section>

    <footer>
        <p>&copy; 2024 GeoRedirect Service. All rights reserved.</p>
        <p>API Version: <?php 
            $config = $conn->query("SELECT configValue FROM site_config WHERE configKey = 'api_version'");
            if ($config && $row = $config->fetch_assoc()) {
                echo htmlspecialchars($row['configValue']);
            }
        ?></p>
    </footer>
</div>
</body>
</html>
<?php $conn->close(); ?>
