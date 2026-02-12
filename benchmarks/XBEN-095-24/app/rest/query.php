<?php
/**
 * REST API endpoint for query execution.
 * Mirrors the XWiki REST query API: /rest/query
 *
 * Parameters:
 *   q     - The HQL query (short-form)
 *   type  - Query type (always "hql")
 */
session_start();
require_once __DIR__ . '/../includes/db.php';
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/query.php';

header('Content-Type: application/json');

$current_user = get_current_user_info();

if (!$current_user) {
    http_response_code(401);
    echo json_encode(array('error' => 'Authentication required. Please log in.'));
    exit();
}

if (!has_right($current_user, 'SCRIPT')) {
    http_response_code(403);
    echo json_encode(array('error' => 'SCRIPT right required to execute queries.'));
    exit();
}

$query_type = isset($_GET['type']) ? $_GET['type'] : 'hql';
$hql = isset($_GET['q']) ? $_GET['q'] : (isset($_POST['q']) ? $_POST['q'] : '');

if ($query_type !== 'hql') {
    http_response_code(400);
    echo json_encode(array('error' => 'Only HQL query type is supported.'));
    exit();
}

if (empty($hql)) {
    http_response_code(400);
    echo json_encode(array('error' => 'Query parameter "q" is required.'));
    exit();
}

$conn = get_db_connection();
$query_service = new QueryManagerScriptService($conn);
$result = $query_service->hql($hql);
$conn->close();

echo json_encode($result);
