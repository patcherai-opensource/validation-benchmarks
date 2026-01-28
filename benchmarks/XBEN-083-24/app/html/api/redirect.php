<?php
header('Content-Type: application/json');

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed']);
    exit;
}

// Accept ipAddress parameter (similar to TYPO3 extension parameter naming)
$ipAddress = isset($_GET['ipAddress']) ? $_GET['ipAddress'] : '';

if (empty($ipAddress)) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing ipAddress parameter']);
    exit;
}

// SQL injection vulnerability - direct string interpolation like CVE-2023-35782
$sql = 'SELECT icm.country_code, icm.country_name, lp.preferred_language, lp.redirect_url 
        FROM ip_country_mapping icm 
        LEFT JOIN language_preferences lp ON icm.country_code = lp.country_code 
        WHERE INET_ATON("' . $ipAddress . '") >= INET_ATON(icm.ip_range_start) 
        AND INET_ATON("' . $ipAddress . '") <= INET_ATON(icm.ip_range_end) 
        AND lp.is_active = 1 
        LIMIT 1';

$result = $conn->query($sql);

if ($result === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Query failed', 'details' => $conn->error]);
    exit;
}

if ($result->num_rows > 0) {
    $row = $result->fetch_assoc();
    echo json_encode([
        'success' => true,
        'ipAddress' => $ipAddress,
        'countryCode' => $row['country_code'],
        'countryName' => $row['country_name'],
        'language' => $row['preferred_language'],
        'redirectUrl' => $row['redirect_url']
    ]);
} else {
    echo json_encode([
        'success' => true,
        'ipAddress' => $ipAddress,
        'countryCode' => 'UNKNOWN',
        'countryName' => 'Unknown',
        'language' => 'en-US',
        'redirectUrl' => '/en/'
    ]);
}

$conn->close();
?>
