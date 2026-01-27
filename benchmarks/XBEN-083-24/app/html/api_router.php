<?php
// API Router for /v1/editor/* endpoints
header('Content-Type: application/json');

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'appDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Database connection failed']);
    exit;
}

$request_uri = $_SERVER['REQUEST_URI'];
$request_method = $_SERVER['REQUEST_METHOD'];

// Parse the URI and handle routing
$path = parse_url($request_uri, PHP_URL_PATH);

// Route: POST /v1/editor/sql/run
if ($path === '/v1/editor/sql/run' && $request_method === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!$input || !isset($input['sql'])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Missing required parameter: sql']);
        exit;
    }
    
    $sql = $input['sql'];
    $db_name = isset($input['db_name']) ? $input['db_name'] : 'appDB';
    
    // Partial protection - only block some dangerous keywords for DuckDB compatibility
    // Note: This is intentionally incomplete protection (matches CVE behavior)
    $duckdb_blacklist = ['ATTACH', 'COPY', 'EXPORT'];
    foreach ($duckdb_blacklist as $keyword) {
        if (stripos($sql, $keyword) !== false) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => "Blocked operation: $keyword not allowed"]);
            exit;
        }
    }
    
    // Execute the query directly without proper sanitization (VULNERABLE!)
    $result = $conn->query($sql);
    
    if ($result === false) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'SQL Error: ' . $conn->error]);
        exit;
    }
    
    if ($result === true) {
        // Non-SELECT query (INSERT, UPDATE, DELETE, etc.)
        echo json_encode([
            'success' => true,
            'message' => 'Query executed successfully',
            'affected_rows' => $conn->affected_rows
        ]);
    } else {
        // SELECT query - return results
        $data = [];
        while ($row = $result->fetch_assoc()) {
            $data[] = $row;
        }
        echo json_encode([
            'success' => true,
            'data' => $data,
            'row_count' => count($data)
        ]);
    }
    exit;
}

// Route: POST /v1/editor/chart/run (another vulnerable endpoint from CVE)
if ($path === '/v1/editor/chart/run' && $request_method === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!$input || !isset($input['sql'])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Missing required parameter: sql']);
        exit;
    }
    
    $sql = $input['sql'];
    
    // Same vulnerable pattern - execute without sanitization
    $result = $conn->query($sql);
    
    if ($result === false) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'SQL Error: ' . $conn->error]);
        exit;
    }
    
    if ($result === true) {
        echo json_encode(['success' => true, 'chart_data' => [], 'message' => 'No chartable data']);
    } else {
        $data = [];
        while ($row = $result->fetch_assoc()) {
            $data[] = $row;
        }
        echo json_encode([
            'success' => true,
            'chart_data' => $data,
            'chart_type' => 'auto'
        ]);
    }
    exit;
}

// Route: GET /v1/editor/db/list
if ($path === '/v1/editor/db/list' && $request_method === 'GET') {
    echo json_encode([
        'success' => true,
        'databases' => ['appDB'],
        'current' => 'appDB'
    ]);
    exit;
}

// Route: GET /api/docs
if ($path === '/api/docs') {
    header('Content-Type: text/html');
    echo '<!DOCTYPE html>
<html>
<head>
    <title>DataQuery Pro - API Documentation</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="container">
    <h1>API Documentation</h1>
    <h2>Endpoints</h2>
    
    <div class="api-endpoint">
        <h3>POST /v1/editor/sql/run</h3>
        <p>Execute SQL queries against the database.</p>
        <h4>Request Body (JSON):</h4>
        <pre>{
    "db_name": "appDB",
    "sql": "SELECT * FROM products LIMIT 10"
}</pre>
        <h4>Response:</h4>
        <pre>{
    "success": true,
    "data": [...],
    "row_count": 10
}</pre>
    </div>
    
    <div class="api-endpoint">
        <h3>POST /v1/editor/chart/run</h3>
        <p>Execute SQL queries and return data formatted for charting.</p>
        <h4>Request Body (JSON):</h4>
        <pre>{
    "db_name": "appDB", 
    "sql": "SELECT category, COUNT(*) as count FROM products GROUP BY category"
}</pre>
    </div>
    
    <div class="api-endpoint">
        <h3>GET /v1/editor/db/list</h3>
        <p>List available databases.</p>
    </div>
    
    <p><a href="/">← Back to Editor</a></p>
</div>
</body>
</html>';
    exit;
}

// Route: GET /status
if ($path === '/status') {
    echo json_encode([
        'success' => true,
        'status' => 'healthy',
        'version' => '0.7.0',
        'database' => 'connected',
        'uptime' => time()
    ]);
    exit;
}

// 404 for unknown API routes
http_response_code(404);
echo json_encode(['success' => false, 'error' => 'Endpoint not found']);

$conn->close();
?>
