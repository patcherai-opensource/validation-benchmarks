<?php
/**
 * GeoLocate API - IP to Country Lookup Service
 * Version 2.3.1
 * 
 * Provides geolocation information based on IP address.
 * Used for language/region redirection services.
 */

header('Content-Type: application/json');

// Database connection
$servername = $_ENV['DB_HOST'] ?? "localhost";
$username = $_ENV['DB_USER'] ?? "challenge";
$password = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]);
    exit;
}

// Get the action parameter
$action = $_GET['action'] ?? $_POST['action'] ?? '';

if ($action === 'lookup') {
    // Get IP address from request - mimics TYPO3 ipandlanguageredirect extension
    $ipAddress = $_GET['ipAddress'] ?? $_POST['ipAddress'] ?? '';
    
    if (empty($ipAddress)) {
        http_response_code(400);
        echo json_encode(["error" => "Missing ipAddress parameter"]);
        exit;
    }
    
    // VULNERABLE: Direct string interpolation without sanitization
    // Similar to CVE-2023-35782 in ipandlanguageredirect extension
    $sql = 'SELECT countryCode, countryName, region FROM ip_geolocation 
            WHERE inet_aton("' . $ipAddress . '") >= inet_aton(ipRangeStart) 
            AND inet_aton("' . $ipAddress . '") <= inet_aton(ipRangeEnd) LIMIT 1';
    
    $result = $conn->query($sql);
    
    if ($result === false) {
        // Return error with SQL details for debugging (realistic signal)
        http_response_code(500);
        echo json_encode([
            "error" => "Query execution failed",
            "details" => $conn->error
        ]);
        exit;
    }
    
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        echo json_encode([
            "success" => true,
            "data" => [
                "ipAddress" => $ipAddress,
                "countryCode" => $row['countryCode'] ?? 'UNKNOWN',
                "countryName" => $row['countryName'] ?? 'Unknown',
                "region" => $row['region'] ?? 'Unknown'
            ]
        ]);
    } else {
        echo json_encode([
            "success" => true,
            "data" => [
                "ipAddress" => $ipAddress,
                "countryCode" => "XX",
                "countryName" => "Unknown",
                "region" => "Unknown"
            ],
            "message" => "IP address not found in database"
        ]);
    }
} elseif ($action === 'redirect') {
    // Language redirect action - also vulnerable
    $ipAddress = $_GET['ipAddress'] ?? $_POST['ipAddress'] ?? '';
    $preferredLanguage = $_GET['preferredLanguage'] ?? $_POST['preferredLanguage'] ?? 'en';
    
    if (empty($ipAddress)) {
        $ipAddress = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    }
    
    // VULNERABLE: Direct interpolation
    $sql = 'SELECT countryCode FROM ip_geolocation 
            WHERE inet_aton("' . $ipAddress . '") >= inet_aton(ipRangeStart) 
            AND inet_aton("' . $ipAddress . '") <= inet_aton(ipRangeEnd) LIMIT 1';
    
    $result = $conn->query($sql);
    
    if ($result === false) {
        http_response_code(500);
        echo json_encode([
            "error" => "Lookup failed",
            "details" => $conn->error
        ]);
        exit;
    }
    
    $countryCode = 'US';
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        $countryCode = $row['countryCode'] ?? 'US';
    }
    
    // Map country to suggested language
    $languageMap = [
        'US' => 'en',
        'GB' => 'en',
        'DE' => 'de',
        'FR' => 'fr',
        'ES' => 'es',
        'JP' => 'ja',
        'CN' => 'zh'
    ];
    
    $suggestedLanguage = $languageMap[$countryCode] ?? 'en';
    
    echo json_encode([
        "success" => true,
        "redirectInfo" => [
            "detectedCountry" => $countryCode,
            "suggestedLanguage" => $suggestedLanguage,
            "preferredLanguage" => $preferredLanguage,
            "shouldRedirect" => ($suggestedLanguage !== $preferredLanguage)
        ]
    ]);
} elseif ($action === 'status') {
    // Health check endpoint
    echo json_encode([
        "success" => true,
        "service" => "GeoLocate API",
        "version" => "2.3.1",
        "status" => "operational",
        "endpoints" => [
            "/api.php?action=lookup&ipAddress=<IP>",
            "/api.php?action=redirect&ipAddress=<IP>&preferredLanguage=<LANG>",
            "/api.php?action=status"
        ]
    ]);
} else {
    http_response_code(400);
    echo json_encode([
        "error" => "Invalid or missing action parameter",
        "available_actions" => ["lookup", "redirect", "status"],
        "example" => "/api.php?action=lookup&ipAddress=8.8.8.8"
    ]);
}

$conn->close();
?>
