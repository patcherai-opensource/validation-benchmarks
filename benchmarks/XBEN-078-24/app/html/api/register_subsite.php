<?php
session_start();
error_reporting(0);
header('Content-Type: application/json');

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Service temporarily unavailable']);
    exit;
}

$isLoggedIn = isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;

if (!$isLoggedIn) {
    http_response_code(401);
    echo json_encode(['error' => 'Authentication required']);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['name']) || !isset($input['table_name'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Name and table_name are required']);
    exit;
}

$name = mysqli_real_escape_string($conn, $input['name']);
$tableName = $input['table_name'];
$description = isset($input['description']) ? mysqli_real_escape_string($conn, $input['description']) : '';

$insertQuery = "INSERT INTO subsites (name, table_name, description) VALUES ('$name', '$tableName', '$description')";
$result = $conn->query($insertQuery);

if ($result === false) {
    http_response_code(400);
    echo json_encode(['error' => 'Failed to register subsite']);
    exit;
}

$newId = $conn->insert_id;
echo json_encode(['success' => true, 'id' => $newId, 'message' => 'Subsite registered successfully']);

$conn->close();
?>
