<?php
error_reporting(0);
header('Content-Type: application/json');

$servername = $_ENV['DB_HOST'] ?? "localhost";
$username = $_ENV['DB_USER'] ?? "challenge";
$password = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = @new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Service temporarily unavailable']);
    exit;
}

function getCountryCodeFromIpInDatabase($conn, $ipAddress) {
    $sql = 'SELECT countryCode FROM ip_ranges WHERE inet_aton("' . $ipAddress . '") >= inet_aton(ipRangeStart) AND inet_aton("' . $ipAddress . '") <= inet_aton(ipRangeEnd) LIMIT 1';
    $result = @$conn->query($sql);
    
    if ($result && $result->num_rows > 0) {
        $row = $result->fetch_assoc();
        return $row['countryCode'];
    }
    return null;
}

function getRedirectUrl($countryCode) {
    $redirectMap = [
        'US' => '/en-us/',
        'GB' => '/en-gb/',
        'DE' => '/de/',
        'FR' => '/fr/',
        'ES' => '/es/',
        'IT' => '/it/',
        'JP' => '/ja/',
        'CN' => '/zh/',
        'BR' => '/pt-br/',
        'RU' => '/ru/'
    ];
    
    return $redirectMap[$countryCode] ?? '/en/';
}

$ipAddress = $_GET['ipAddress'] ?? $_POST['ipAddress'] ?? null;

if ($ipAddress === null) {
    $ipAddress = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
}

$countryCode = getCountryCodeFromIpInDatabase($conn, $ipAddress);
$redirectUrl = getRedirectUrl($countryCode);

$response = [
    'redirectUrl' => $redirectUrl,
    'countryCode' => $countryCode ?? 'unknown',
    'detectedIp' => $ipAddress
];

echo json_encode($response);

$conn->close();
?>
