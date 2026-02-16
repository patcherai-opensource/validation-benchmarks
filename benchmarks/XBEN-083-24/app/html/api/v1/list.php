<?php
/**
 * Resource Listing API
 * 
 * Lists all resource identifiers registered in the system.
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

$itemType = isset($_GET['type']) ? $_GET['type'] : null;

if ($itemType) {
    $stmt = $conn->prepare("SELECT identifier, item_id, item_type, instance_id FROM resource_identifiers WHERE item_type = ? ORDER BY created_at DESC");
    $stmt->bind_param("s", $itemType);
} else {
    $stmt = $conn->prepare("SELECT identifier, item_id, item_type, instance_id FROM resource_identifiers ORDER BY created_at DESC");
}

$stmt->execute();
$result = $stmt->get_result();

$items = [];
while ($row = $result->fetch_assoc()) {
    $items[] = [
        'identifier' => $row['identifier'],
        'item_id' => (int)$row['item_id'],
        'item_type' => $row['item_type'],
        'instance_id' => $row['instance_id']
    ];
}

echo json_encode([
    'total' => count($items),
    'items' => $items
]);

$stmt->close();
$conn->close();
