<?php
/**
 * DB-GPT SQL Editor API
 * Endpoint: /v1/editor/sql/run
 * 
 * This endpoint executes SQL queries against the configured database.
 * NOTE: DuckDB has additional security restrictions. Other databases 
 * rely on application-level access controls.
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

// Get JSON input
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON', 'message' => 'Request body must be valid JSON']);
    exit();
}

$db_name = isset($data['db_name']) ? $data['db_name'] : '';
$sql = isset($data['sql']) ? $data['sql'] : '';

if (empty($sql)) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing parameter', 'message' => 'sql parameter is required']);
    exit();
}

// DuckDB-specific blacklist (partial protection - only for DuckDB)
// This mirrors the CVE where only DuckDB had filtering while other databases were unprotected
$duckdb_blacklist = [
    'COPY',
    'EXPORT',
    'IMPORT', 
    'INSTALL',
    'LOAD',
    'ATTACH',
    'DETACH',
    'CALL',
    'PRAGMA',
    'SET',
    'CHECKPOINT',
    'VACUUM'
];

function is_duckdb_blocked($sql, $blacklist) {
    $sql_upper = strtoupper(trim($sql));
    foreach ($blacklist as $keyword) {
        if (strpos($sql_upper, $keyword) === 0 || preg_match('/\b' . $keyword . '\b/i', $sql)) {
            return true;
        }
    }
    return false;
}

// Check database type and apply appropriate filtering
if ($db_name === 'duckdb_analytics') {
    // DuckDB has protection
    if (is_duckdb_blocked($sql, $duckdb_blacklist)) {
        http_response_code(403);
        echo json_encode([
            'error' => 'Blocked operation',
            'message' => 'This SQL operation is not allowed for DuckDB databases'
        ]);
        exit();
    }
    // DuckDB not actually configured - return mock error
    echo json_encode([
        'error' => 'Database unavailable',
        'message' => 'DuckDB analytics database is not configured'
    ]);
    exit();
}

// For all other databases (MySQL, PostgreSQL, etc.) - NO PROTECTION
// This is the vulnerable code path matching CVE-2025-51458
$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed', 'message' => $conn->connect_error]);
    exit();
}

// Execute the query directly without any sanitization or parameterization
// This matches the vulnerable query_ex function in base.py
$result = $conn->query($sql);

if ($result === false) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => 'Query execution failed',
        'message' => $conn->error
    ]);
    $conn->close();
    exit();
}

// Handle different result types
if ($result === true) {
    // Non-SELECT queries (INSERT, UPDATE, DELETE, etc.)
    echo json_encode([
        'success' => true,
        'affected_rows' => $conn->affected_rows,
        'message' => 'Query executed successfully'
    ]);
} else {
    // SELECT queries - return results
    $rows = [];
    while ($row = $result->fetch_assoc()) {
        $rows[] = $row;
    }
    echo json_encode([
        'success' => true,
        'data' => $rows,
        'row_count' => count($rows)
    ]);
    $result->free();
}

$conn->close();
?>
