<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'geoserviceDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - GeoRedirect Service</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header>
        <h1>GeoRedirect Service</h1>
        <p class="tagline">API Documentation</p>
        <nav>
            <a href="/">Home</a>
            <a href="/api.php">API</a>
            <a href="/documentation.php">Documentation</a>
        </nav>
    </header>

    <section class="documentation">
        <h2>API Reference</h2>
        
        <div class="endpoint-doc">
            <h3>IP Lookup</h3>
            <p class="method">GET /api.php?type=lookup</p>
            <h4>Parameters</h4>
            <ul>
                <li><code>tx_ipandlanguageredirect_pi1[ipAddress]</code> - The IP address to look up</li>
                <li><code>ipAddress</code> - Alternative parameter name for the IP address</li>
            </ul>
            <h4>Response</h4>
            <pre>{
    "ipAddress": "8.8.8.8",
    "countryCode": "US"
}</pre>
            <h4>Example</h4>
            <pre>GET /api.php?type=lookup&tx_ipandlanguageredirect_pi1[ipAddress]=8.8.8.8</pre>
        </div>

        <div class="endpoint-doc">
            <h3>Redirect Info</h3>
            <p class="method">GET /api.php?type=redirect</p>
            <h4>Parameters</h4>
            <ul>
                <li><code>tx_ipandlanguageredirect_pi1[ipAddress]</code> - The IP address to look up</li>
            </ul>
            <h4>Response</h4>
            <pre>{
    "ipAddress": "8.8.8.8",
    "countryCode": "US",
    "preferredLanguage": "en-US",
    "redirectUrl": "/en/"
}</pre>
        </div>

        <div class="endpoint-doc">
            <h3>List Languages</h3>
            <p class="method">GET /api.php?type=languages</p>
            <h4>Response</h4>
            <pre>{
    "languages": [
        {"countryCode": "US", "preferredLanguage": "en-US", "redirectUrl": "/en/"},
        ...
    ]
}</pre>
        </div>

        <div class="endpoint-doc">
            <h3>Get Configuration</h3>
            <p class="method">GET /api.php?type=config</p>
            <h4>Response</h4>
            <pre>{
    "config": {
        "site_name": "GeoRedirect Service",
        "default_language": "en-US",
        ...
    }
}</pre>
        </div>
    </section>

    <section class="integration">
        <h2>Integration Guide</h2>
        <p>To integrate this service with your TYPO3 installation, add the following to your TypoScript:</p>
        <pre>
plugin.tx_ipandlanguageredirect_pi1 {
    settings {
        redirectMode = http
        apiEndpoint = /api.php?type=redirect
    }
}
        </pre>
        <p>The service will automatically detect visitor IPs and redirect them to the appropriate language version.</p>
    </section>

    <footer>
        <p>&copy; 2024 GeoRedirect Service. All rights reserved.</p>
    </footer>
</div>
</body>
</html>
<?php if ($conn) $conn->close(); ?>
