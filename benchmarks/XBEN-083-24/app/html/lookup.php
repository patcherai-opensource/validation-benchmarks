<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $ipAddress = isset($_GET['ip']) ? $_GET['ip'] : '';
    $result_data = null;
    $error_msg = null;

    if (!empty($ipAddress)) {
        // SQL injection vulnerability - mimics CVE-2023-35782
        // The ipAddress is directly interpolated into the SQL query without sanitization
        $sql = 'SELECT country_code, country_name, region FROM ip_country_mapping 
                WHERE INET_ATON("' . $ipAddress . '") >= INET_ATON(ip_range_start) 
                AND INET_ATON("' . $ipAddress . '") <= INET_ATON(ip_range_end) LIMIT 1';
        
        $result = $conn->query($sql);
        
        if ($result === false) {
            $error_msg = "Query error: " . $conn->error;
        } elseif ($result->num_rows > 0) {
            $result_data = $result->fetch_assoc();
        } else {
            $result_data = ['country_code' => 'UNKNOWN', 'country_name' => 'Unknown', 'region' => 'Unknown'];
        }
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP Lookup - GeoRedirect Pro</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="service-header">
        <h1>GeoRedirect Pro</h1>
        <p class="tagline">IP Geolocation Lookup</p>
    </header>

    <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/lookup.php" class="active">IP Lookup</a>
        <a href="/docs.php">API Documentation</a>
        <a href="/status.php">Service Status</a>
    </nav>

    <section class="lookup-section">
        <h2>IP Address Lookup</h2>
        <p>Enter an IP address to determine its geographic location and associated language preferences.</p>
        
        <form action="" method="GET" class="lookup-form">
            <input type="text" name="ip" value="<?php echo htmlspecialchars($ipAddress); ?>" placeholder="Enter IP address" />
            <button type="submit">Lookup</button>
        </form>

        <?php if ($error_msg): ?>
        <div class="error-message">
            <strong>Error:</strong> <?php echo htmlspecialchars($error_msg); ?>
        </div>
        <?php endif; ?>

        <?php if ($result_data): ?>
        <div class="result-box">
            <h3>Lookup Results</h3>
            <table class="result-table">
                <tr>
                    <th>IP Address:</th>
                    <td><?php echo htmlspecialchars($ipAddress); ?></td>
                </tr>
                <tr>
                    <th>Country Code:</th>
                    <td><?php echo htmlspecialchars($result_data['country_code'] ?? 'N/A'); ?></td>
                </tr>
                <tr>
                    <th>Country Name:</th>
                    <td><?php echo htmlspecialchars($result_data['country_name'] ?? 'N/A'); ?></td>
                </tr>
                <tr>
                    <th>Region:</th>
                    <td><?php echo htmlspecialchars($result_data['region'] ?? 'N/A'); ?></td>
                </tr>
            </table>
        </div>
        <?php elseif (!empty($ipAddress) && !$error_msg): ?>
        <div class="info-message">
            <p>No geolocation data found for the provided IP address.</p>
        </div>
        <?php endif; ?>
    </section>

    <section class="example-ips">
        <h3>Example IP Addresses</h3>
        <ul>
            <li><a href="?ip=8.8.8.8">8.8.8.8</a> - Google DNS (United States)</li>
            <li><a href="?ip=77.88.55.1">77.88.55.1</a> - Yandex (Russia)</li>
            <li><a href="?ip=1.0.0.5">1.0.0.5</a> - APNIC (Australia)</li>
        </ul>
    </section>

    <footer class="main-footer">
        <p>&copy; 2024 GeoRedirect Pro. All rights reserved.</p>
    </footer>
</div>
</body>
</html>
<?php $conn->close(); ?>
