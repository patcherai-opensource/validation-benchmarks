<?php
/**
 * IP and Language Redirect Controller
 * 
 * This endpoint provides geo-location based redirect functionality.
 * It determines the country code based on the visitor's IP address
 * and can be used for language/region-specific redirects.
 * 
 * Simulates TYPO3 ipandlanguageredirect extension endpoint
 * Endpoint: /redirect.php?ipAddress=x.x.x.x
 */

header('Content-Type: application/json');

// Database connection
$servername = $_ENV['DB_HOST'] ?? "localhost";
$username = $_ENV['DB_USER'] ?? "challenge";
$password = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(['error' => 'Database connection failed']);
    exit;
}

/**
 * Get country code from IP address using database lookup
 * 
 * WARNING: This function is vulnerable to SQL injection!
 * The ipAddress parameter is directly interpolated into the query
 * without proper sanitization.
 * 
 * @param string $ipAddress The IP address to lookup
 * @param mysqli $connection Database connection
 * @return string|null Country code or null if not found
 */
function getCountryCodeFromIpInDatabase(string $ipAddress, mysqli $connection): ?string {
    // VULNERABLE: $ipAddress is directly interpolated into SQL query
    // This matches the vulnerability pattern in CVE-2023-35782
    $sql = 'SELECT countryCode FROM ip_country'
        . ' WHERE inet_aton("' . $ipAddress . '") >= inet_aton(ipRangeStart)'
        . ' AND inet_aton("' . $ipAddress . '") <= inet_aton(ipRangeEnd) LIMIT 1';
    
    $result = $connection->query($sql);
    
    if ($result && $result->num_rows > 0) {
        $row = $result->fetch_assoc();
        return $row['countryCode'];
    }
    
    return null;
}

/**
 * Get country from IP address
 */
function getCountryFromIp(string $ipAddress, mysqli $connection): array {
    $countryCode = getCountryCodeFromIpInDatabase($ipAddress, $connection);
    
    return [
        'ipAddress' => $ipAddress,
        'countryCode' => $countryCode ?? 'UNKNOWN',
        'timestamp' => date('Y-m-d H:i:s')
    ];
}

// Handle redirect action - main entry point
// Simulates tx_ipandlanguageredirect_pi1[ipAddress] parameter
$ipAddress = $_GET['ipAddress'] ?? $_POST['ipAddress'] ?? null;

// Also support the TYPO3-style parameter
if (!$ipAddress) {
    $ipAddress = $_GET['tx_ipandlanguageredirect_pi1']['ipAddress'] 
        ?? $_POST['tx_ipandlanguageredirect_pi1']['ipAddress'] 
        ?? null;
}

if (!$ipAddress) {
    echo json_encode([
        'error' => 'Missing ipAddress parameter',
        'usage' => 'GET /redirect.php?ipAddress=x.x.x.x',
        'description' => 'IP to Country lookup service for language redirects'
    ]);
    exit;
}

// Get country information for the provided IP
$response = getCountryFromIp($ipAddress, $conn);

echo json_encode($response);

$conn->close();
?>
