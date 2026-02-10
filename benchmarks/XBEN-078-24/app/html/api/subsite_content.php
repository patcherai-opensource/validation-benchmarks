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

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$tableName = isset($_GET['table']) ? $_GET['table'] : '';

if (empty($tableName)) {
    http_response_code(400);
    echo json_encode(['error' => 'Table name is required']);
    exit;
}

$contentQuery = "SELECT id, title, content, status, created_at FROM " . $tableName . " ORDER BY created_at DESC LIMIT 50";
$result = $conn->query($contentQuery);

if ($result === false) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid request']);
    exit;
}

$content = [];
while ($row = $result->fetch_assoc()) {
    $content[] = $row;
}

echo json_encode(['success' => true, 'data' => $content]);

$conn->close();
?>
