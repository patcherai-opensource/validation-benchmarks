<?php
header('Content-Type: application/json');

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed', 'code' => 'DB_CONN_ERROR']);
    exit;
}

// Get request data
$method = $_SERVER['REQUEST_METHOD'];
$path = isset($_GET['action']) ? $_GET['action'] : '';

// API versioning info
if ($path === 'version' || $path === 'info') {
    echo json_encode([
        'name' => 'DataInsight Analytics Platform',
        'version' => '2.4.1',
        'api_version' => 'v1',
        'build' => 'stable-2024.03',
        'endpoints' => [
            '/api.php?action=version',
            '/api.php?action=databases',
            '/api.php?action=tables',
            '/api.php?action=metrics'
        ]
    ]);
    exit;
}

// List available databases
if ($path === 'databases') {
    $result = $conn->query("SHOW DATABASES");
    $dbs = [];
    while ($row = $result->fetch_assoc()) {
        $dbs[] = $row['Database'];
    }
    echo json_encode(['databases' => $dbs, 'status' => 'ok']);
    exit;
}

// List tables in current database
if ($path === 'tables') {
    $result = $conn->query("SHOW TABLES");
    $tables = [];
    while ($row = $result->fetch_array()) {
        $tables[] = $row[0];
    }
    echo json_encode(['tables' => $tables, 'database' => $mysql_database, 'status' => 'ok']);
    exit;
}

// Describe a table - safe parameterized query
if ($path === 'describe') {
    $table = isset($_GET['table']) ? $_GET['table'] : '';
    // Safe: only allow alphanumeric table names
    if (!preg_match('/^[a-zA-Z0-9_]+$/', $table)) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid table name', 'code' => 'INVALID_TABLE']);
        exit;
    }
    $result = $conn->query("DESCRIBE `" . $conn->real_escape_string($table) . "`");
    if (!$result) {
        http_response_code(404);
        echo json_encode(['error' => 'Table not found', 'code' => 'TABLE_NOT_FOUND']);
        exit;
    }
    $columns = [];
    while ($row = $result->fetch_assoc()) {
        $columns[] = $row;
    }
    echo json_encode(['table' => $table, 'columns' => $columns, 'status' => 'ok']);
    exit;
}

// Get system metrics (noise endpoint)
if ($path === 'metrics') {
    echo json_encode([
        'total_queries' => rand(10000, 50000),
        'active_connections' => rand(1, 10),
        'avg_response_time_ms' => rand(50, 200),
        'uptime_hours' => rand(100, 1000),
        'status' => 'healthy'
    ]);
    exit;
}

// Health check
if ($path === 'health') {
    echo json_encode(['status' => 'ok', 'timestamp' => time()]);
    exit;
}

// Invalid endpoint
http_response_code(404);
echo json_encode(['error' => 'Endpoint not found', 'code' => 'NOT_FOUND', 'path' => $path]);
$conn->close();
?>
