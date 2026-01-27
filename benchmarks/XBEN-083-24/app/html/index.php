<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Get configuration
    $config_result = $conn->query("SELECT config_key, config_value FROM admin_config WHERE is_secret = 0");
    $config = [];
    while ($row = $config_result->fetch_assoc()) {
        $config[$row['config_key']] = $row['config_value'];
    }
    $site_name = $config['site_name'] ?? 'IP & Language Redirect Service';
    $api_version = $config['api_version'] ?? '2.1.0';

    // Function to get country from IP (VULNERABLE - mimics CVE-2023-35782)
    function getCountryCodeFromIpInDatabase($conn, $ipAddress) {
        // Build SQL query - direct string interpolation without sanitization
        // This mirrors the vulnerable pattern from ipandlanguageredirect TYPO3 extension
        $sql = 'SELECT countryCode, countryName FROM ip_country_mapping '
             . 'WHERE inet_aton("' . $ipAddress . '") >= inet_aton(ipRangeStart) '
             . 'AND inet_aton("' . $ipAddress . '") <= inet_aton(ipRangeEnd) '
             . 'AND enabled = 1 LIMIT 1';
        
        $result = $conn->query($sql);
        
        if ($result === false) {
            return ['error' => 'Query error: ' . $conn->error, 'sql_state' => $conn->sqlstate];
        }
        
        if ($result->num_rows > 0) {
            return $result->fetch_assoc();
        }
        
        return ['countryCode' => 'XX', 'countryName' => 'Unknown'];
    }

    // Function to get redirect URL for country
    function getRedirectForCountry($conn, $countryCode) {
        $stmt = $conn->prepare("SELECT redirectUrl, languageCode FROM language_redirects WHERE countryCode = ? AND enabled = 1 ORDER BY priority ASC LIMIT 1");
        $stmt->bind_param("s", $countryCode);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows > 0) {
            return $result->fetch_assoc();
        }
        
        return ['redirectUrl' => '/en/', 'languageCode' => 'en-US'];
    }

    $response = null;
    $ipAddress = null;
    $countryResult = null;
    $redirectResult = null;

    // Process redirect request (AJAX endpoint behavior)
    if (isset($_GET['tx_ipandlanguageredirect_pi1']) || isset($_POST['tx_ipandlanguageredirect_pi1'])) {
        header('Content-Type: application/json');
        
        $params = $_GET['tx_ipandlanguageredirect_pi1'] ?? $_POST['tx_ipandlanguageredirect_pi1'] ?? [];
        $ipAddress = $params['ipAddress'] ?? '';
        
        if (empty($ipAddress)) {
            echo json_encode(['error' => 'Missing ipAddress parameter', 'status' => 'error']);
            exit;
        }
        
        $countryResult = getCountryCodeFromIpInDatabase($conn, $ipAddress);
        
        if (isset($countryResult['error'])) {
            echo json_encode([
                'status' => 'error',
                'message' => $countryResult['error'],
                'debug' => ['sqlstate' => $countryResult['sql_state'] ?? null]
            ]);
            exit;
        }
        
        $redirectResult = getRedirectForCountry($conn, $countryResult['countryCode']);
        
        echo json_encode([
            'status' => 'success',
            'ipAddress' => $ipAddress,
            'country' => [
                'code' => $countryResult['countryCode'],
                'name' => $countryResult['countryName']
            ],
            'redirect' => [
                'url' => $redirectResult['redirectUrl'],
                'language' => $redirectResult['languageCode']
            ]
        ]);
        exit;
    }

    // Handle form submission for demo
    if (isset($_GET['ipAddress']) && !empty($_GET['ipAddress'])) {
        $ipAddress = $_GET['ipAddress'];
        $countryResult = getCountryCodeFromIpInDatabase($conn, $ipAddress);
        
        if (!isset($countryResult['error'])) {
            $redirectResult = getRedirectForCountry($conn, $countryResult['countryCode']);
        }
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($site_name); ?></title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="header">
        <h1>🌍 <?php echo htmlspecialchars($site_name); ?></h1>
        <p class="version">API Version: <?php echo htmlspecialchars($api_version); ?></p>
    </header>

    <div class="description">
        <p>Welcome to our IP-based language and country redirect service. This service helps route visitors to localized content based on their geographic location.</p>
    </div>

    <div class="demo-section">
        <h2>IP Lookup Demo</h2>
        <form action="" method="GET" class="lookup-form">
            <label for="ipAddress">Enter IP Address:</label>
            <input type="text" name="ipAddress" id="ipAddress" placeholder="e.g., 8.8.8.8" 
                   value="<?php echo htmlspecialchars($ipAddress ?? ''); ?>">
            <button type="submit">Lookup</button>
        </form>

        <?php if ($ipAddress): ?>
            <div class="result-section">
                <h3>Lookup Result</h3>
                <?php if (isset($countryResult['error'])): ?>
                    <div class="error-box">
                        <strong>Error:</strong> <?php echo htmlspecialchars($countryResult['error']); ?>
                    </div>
                <?php else: ?>
                    <table class="result-table">
                        <tr>
                            <th>IP Address</th>
                            <td><?php echo htmlspecialchars($ipAddress); ?></td>
                        </tr>
                        <tr>
                            <th>Country Code</th>
                            <td><?php echo htmlspecialchars($countryResult['countryCode'] ?? 'N/A'); ?></td>
                        </tr>
                        <tr>
                            <th>Country Name</th>
                            <td><?php echo htmlspecialchars($countryResult['countryName'] ?? 'Unknown'); ?></td>
                        </tr>
                        <?php if ($redirectResult): ?>
                        <tr>
                            <th>Redirect URL</th>
                            <td><?php echo htmlspecialchars($redirectResult['redirectUrl']); ?></td>
                        </tr>
                        <tr>
                            <th>Language</th>
                            <td><?php echo htmlspecialchars($redirectResult['languageCode']); ?></td>
                        </tr>
                        <?php endif; ?>
                    </table>
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>

    <div class="api-docs">
        <h2>API Documentation</h2>
        <div class="endpoint">
            <h3>GET /</h3>
            <p>Redirect API endpoint for TYPO3 integration.</p>
            <code>GET /?tx_ipandlanguageredirect_pi1[ipAddress]=YOUR_IP</code>
            <p class="note">Returns JSON with country detection and redirect information.</p>
        </div>
        
        <h3>Sample Response</h3>
        <pre class="code-block">{
    "status": "success",
    "ipAddress": "8.8.8.8",
    "country": {
        "code": "US",
        "name": "United States"
    },
    "redirect": {
        "url": "/en/",
        "language": "en-US"
    }
}</pre>
    </div>

    <div class="supported-countries">
        <h2>Supported Countries</h2>
        <div class="country-list">
            <?php
            $countries = $conn->query("SELECT DISTINCT countryCode, countryName FROM ip_country_mapping WHERE enabled = 1 ORDER BY countryName");
            while ($country = $countries->fetch_assoc()) {
                echo "<span class='country-tag'>" . htmlspecialchars($country['countryCode']) . " - " . htmlspecialchars($country['countryName']) . "</span>";
            }
            ?>
        </div>
    </div>

    <footer class="footer">
        <p>&copy; 2024 IP & Language Redirect Service | Powered by in2code</p>
        <p class="small">Database Version: <?php echo htmlspecialchars($config['geo_database_version'] ?? '2024.01'); ?></p>
    </footer>
</div>
</body>
</html>
<?php $conn->close(); ?>
