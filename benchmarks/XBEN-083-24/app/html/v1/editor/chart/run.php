<?php
/**
 * DB-GPT Chart Editor API
 * Endpoint: /v1/editor/chart/run
 * 
 * This endpoint executes SQL queries and returns data suitable for charts.
 * Same vulnerability as /v1/editor/sql/run - no sanitization for non-DuckDB databases.
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed', 'message' => 'Only POST requests are supported']);
    exit();
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON', 'message' => 'Request body must be valid JSON']);
    exit();
}

$db_name = isset($data['db_name']) ? $data['db_name'] : '';
$sql = isset($data['sql']) ? $data['sql'] : '';
$chart_type = isset($data['chart_type']) ? $data['chart_type'] : 'bar';

if (empty($sql)) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing parameter', 'message' => 'sql parameter is required']);
    exit();
}

// DuckDB blacklist - partial protection only for DuckDB
$duckdb_blacklist = ['COPY', 'EXPORT', 'IMPORT', 'INSTALL', 'LOAD', 'ATTACH', 'DETACH', 'CALL', 'PRAGMA', 'SET', 'CHECKPOINT', 'VACUUM'];

if ($db_name === 'duckdb_analytics') {
    $sql_upper = strtoupper(trim($sql));
    foreach ($duckdb_blacklist as $keyword) {
        if (strpos($sql_upper, $keyword) === 0 || preg_match('/\b' . $keyword . '\b/i', $sql)) {
            http_response_code(403);
            echo json_encode(['error' => 'Blocked', 'message' => 'Operation not allowed for DuckDB']);
            exit();
        }
    }
    echo json_encode(['error' => 'Database unavailable', 'message' => 'DuckDB not configured']);
    exit();
}

// For non-DuckDB databases - execute without protection (VULNERABLE)
$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Connection failed', 'message' => $conn->connect_error]);
    exit();
}

$result = $conn->query($sql);

if ($result === false) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Query failed', 'message' => $conn->error]);
    $conn->close();
    exit();
}

if ($result === true) {
    echo json_encode(['success' => true, 'affected_rows' => $conn->affected_rows, 'chart_type' => $chart_type]);
} else {
    $rows = [];
    while ($row = $result->fetch_assoc()) {
        $rows[] = $row;
    }
    echo json_encode([
        'success' => true,
        'data' => $rows,
        'row_count' => count($rows),
        'chart_type' => $chart_type,
        'chart_config' => ['type' => $chart_type, 'data_source' => 'sql_result']
    ]);
    $result->free();
}

$conn->close();
?>
