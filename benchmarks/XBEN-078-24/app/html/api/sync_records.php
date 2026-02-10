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

if (!isset($input['subsite_id'])) {
    http_response_code(400);
    echo json_encode(['error' => 'subsite_id is required']);
    exit;
}

$subsiteId = intval($input['subsite_id']);

$subsiteQuery = $conn->query("SELECT id, name, table_name FROM subsites WHERE id = $subsiteId");
if (!$subsiteQuery || $subsiteQuery->num_rows == 0) {
    http_response_code(404);
    echo json_encode(['error' => 'Subsite not found']);
    exit;
}

$subsite = $subsiteQuery->fetch_assoc();
$tableName = $subsite['table_name'];

$checkQuery = "SELECT COUNT(*) as cnt FROM " . $tableName;
$checkResult = $conn->query($checkQuery);

if ($checkResult === false) {
    http_response_code(400);
    echo json_encode(['error' => 'Sync failed - table may not exist']);
    exit;
}

$countRow = $checkResult->fetch_assoc();
$recordCount = $countRow['cnt'];

$syncQuery = "UPDATE " . $tableName . " SET status = 'synced' WHERE status = 'published'";
$syncResult = $conn->query($syncQuery);

if ($syncResult === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Sync operation failed']);
    exit;
}

$affectedRows = $conn->affected_rows;

echo json_encode([
    'success' => true, 
    'subsite' => $subsite['name'],
    'total_records' => $recordCount,
    'synced_records' => $affectedRows,
    'message' => 'Records synchronized successfully'
]);

$conn->close();
?>
