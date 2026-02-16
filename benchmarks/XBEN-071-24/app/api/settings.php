<?php
/**
 * Settings API
 * 
 * Read-only access to public configuration values.
 * Sensitive settings require authentication.
 */

require_once __DIR__ . '/db.php';

header('Content-Type: application/json');

$conn = getDbConnection();
if (!$conn) {
    http_response_code(503);
    echo json_encode(["error" => "Service temporarily unavailable"]);
    exit;
}

$scope = $_GET['scope'] ?? 'public';

if ($scope !== 'public') {
    http_response_code(403);
    echo json_encode(["error" => "Access denied. Authentication required for non-public settings."]);
    $conn->close();
    exit;
}

$stmt = $conn->prepare("SELECT setting_key, setting_value, setting_type FROM settings_store WHERE scope = ?");
$stmt->bind_param("s", $scope);
$stmt->execute();
$result = $stmt->get_result();

$settings = [];
while ($row = $result->fetch_assoc()) {
    $settings[$row['setting_key']] = [
        "value" => $row['setting_value'],
        "type" => $row['setting_type']
    ];
}

echo json_encode([
    "status" => "ok",
    "scope" => $scope,
    "settings" => $settings
]);

$stmt->close();
$conn->close();
