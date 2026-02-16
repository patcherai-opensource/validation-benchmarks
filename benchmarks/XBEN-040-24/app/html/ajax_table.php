<?php
require_once 'includes/auth.php';

if (!is_authenticated()) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

header('Content-Type: application/json');

$conn = get_db_connection();

$table_id = isset($_REQUEST['id']) ? basename($_REQUEST['id']) : '';
$current = isset($_REQUEST['current']) ? intval($_REQUEST['current']) : 1;
$rowCount = isset($_REQUEST['rowCount']) ? intval($_REQUEST['rowCount']) : 50;

$response = ['current' => $current, 'rowCount' => $rowCount, 'rows' => [], 'total' => 0];

$allowed_tables = ['hw-lookup', 'ip-lookup'];

if (in_array($table_id, $allowed_tables)) {
    $table_file = "includes/tables/{$table_id}.inc.php";
    if (file_exists($table_file)) {
        include $table_file;
    }
}

echo json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
$conn->close();
