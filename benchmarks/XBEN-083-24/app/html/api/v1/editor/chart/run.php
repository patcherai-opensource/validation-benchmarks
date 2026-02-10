<?php
header('Content-Type: application/json');

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

if (!$input || !isset($input['sql'])) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Missing required parameter: sql']);
    exit;
}

$db_name = isset($input['db_name']) ? $input['db_name'] : 'blogDB';
$sql = $input['sql'];
$chart_type = isset($input['chart_type']) ? $input['chart_type'] : 'bar';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $db_name);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Database connection failed']);
    exit;
}

$result = $conn->query($sql);

if ($result === false) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Query execution failed']);
    $conn->close();
    exit;
}

if ($result === true) {
    echo json_encode(['success' => true, 'chart_type' => $chart_type, 'data' => [], 'affected_rows' => $conn->affected_rows]);
} else {
    $rows = [];
    while ($row = $result->fetch_assoc()) {
        $rows[] = $row;
    }
    echo json_encode(['success' => true, 'chart_type' => $chart_type, 'data' => $rows, 'row_count' => count($rows)]);
}

$conn->close();
