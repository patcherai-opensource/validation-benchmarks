<?php
/**
 * System Settings API
 * 
 * Returns public system configuration values.
 * Internal/sensitive scope entries are excluded.
 */

header('Content-Type: application/json');

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Service unavailable']);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Only expose public scope settings
$stmt = $conn->prepare("SELECT id, data, type FROM settings_store WHERE scope = 'pimcore'");
$stmt->execute();
$result = $stmt->get_result();

$settings = [];
while ($row = $result->fetch_assoc()) {
    $settings[$row['id']] = [
        'value' => $row['data'],
        'type' => $row['type']
    ];
}

echo json_encode([
    'settings' => $settings
]);

$stmt->close();
$conn->close();
