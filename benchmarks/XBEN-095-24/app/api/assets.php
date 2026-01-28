<?php
header('Content-Type: application/json');

$servername = getenv('MYSQL_HOST');
$username = getenv('MYSQL_USER');
$password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed']);
    exit;
}

// Using prepared statement for security
$stmt = $conn->prepare("SELECT id, uuid, asset_name, asset_type, status FROM assets WHERE status = ?");
$status = 'public';
$stmt->bind_param("s", $status);
$stmt->execute();
$result = $stmt->get_result();

$assets = [];
while ($row = $result->fetch_assoc()) {
    $assets[] = [
        'id' => $row['id'],
        'uuid' => $row['uuid'],
        'name' => $row['asset_name'],
        'type' => $row['asset_type'],
        'status' => $row['status']
    ];
}

echo json_encode(['assets' => $assets, 'count' => count($assets)], JSON_PRETTY_PRINT);

$stmt->close();
$conn->close();
?>
