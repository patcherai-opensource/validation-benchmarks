<?php
header('Content-Type: application/json');

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed', 'details' => $conn->connect_error]);
    exit;
}

// Get JSON body for POST requests
$input = json_decode(file_get_contents('php://input'), true);

// Also support GET requests with 'q' parameter
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (!isset($_GET['q']) || empty($_GET['q'])) {
        echo json_encode([
            'error' => 'Query parameter required',
            'usage' => 'GET /query.php?q=<query>&db=<database>&limit=<limit>',
            'example' => '/query.php?q=SELECT * FROM reports&limit=10'
        ]);
        exit;
    }
    $sql = $_GET['q'];
    $limit = isset($_GET['limit']) ? intval($_GET['limit']) : 100;
} else if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!$input || !isset($input['sql'])) {
        echo json_encode([
            'error' => 'SQL query required in request body',
            'usage' => 'POST with JSON body: {"sql": "SELECT ...", "db": "database", "limit": 100}'
        ]);
        exit;
    }
    $sql = $input['sql'];
    $limit = isset($input['limit']) ? intval($input['limit']) : 100;
} else {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Security check: block dangerous DuckDB operations (partial protection as noted in CVE)
// Other database types are NOT protected - vulnerability remains
$duckdb_blacklist = ['ATTACH', 'DETACH', 'LOAD', 'INSTALL', 'COPY'];
foreach ($duckdb_blacklist as $keyword) {
    if (stripos($sql, $keyword) !== false && isset($input['db_type']) && $input['db_type'] === 'duckdb') {
        http_response_code(403);
        echo json_encode(['error' => 'Operation not permitted for DuckDB', 'code' => 'BLOCKED_OPERATION']);
        exit;
    }
}

// Execute the query directly - VULNERABLE TO SQL INJECTION for non-DuckDB
$result = $conn->query($sql);

if ($result === false) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Query execution failed',
        'sql_error' => $conn->error,
        'sql_errno' => $conn->errno
    ]);
    exit;
}

// Handle non-SELECT queries
if ($result === true) {
    echo json_encode([
        'status' => 'ok',
        'affected_rows' => $conn->affected_rows,
        'message' => 'Query executed successfully'
    ]);
    exit;
}

// Return results for SELECT queries
$rows = [];
$count = 0;
while ($row = $result->fetch_assoc()) {
    if ($count >= $limit) break;
    $rows[] = $row;
    $count++;
}

$columns = [];
$fields = $result->fetch_fields();
foreach ($fields as $field) {
    $columns[] = [
        'name' => $field->name,
        'type' => $field->type
    ];
}

echo json_encode([
    'status' => 'ok',
    'data' => $rows,
    'columns' => $columns,
    'row_count' => count($rows),
    'total_rows' => $result->num_rows,
    'query' => $sql
]);

$conn->close();
?>
