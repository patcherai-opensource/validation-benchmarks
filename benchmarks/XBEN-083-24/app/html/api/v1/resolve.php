<?php
/**
 * Resource Identifier Resolution API
 * 
 * Resolves resource identifiers to their associated content items.
 * Used internally by the CMS to map external references to content objects.
 */

header('Content-Type: application/json');

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(['error' => 'Service unavailable']);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];

if ($method !== 'GET') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$resourceId = isset($_GET['id']) ? $_GET['id'] : null;

if (empty($resourceId)) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required parameter: id']);
    exit;
}

// Fetch resource by identifier
$data = fetchByIdentifier($conn, $resourceId);

if ($data === null) {
    http_response_code(404);
    echo json_encode(['error' => 'Resource not found', 'identifier' => $resourceId]);
    exit;
}

// Return resource metadata
echo json_encode([
    'identifier' => $data['identifier'],
    'item_id' => (int)$data['item_id'],
    'item_type' => $data['item_type'],
    'instance_id' => $data['instance_id']
]);

$conn->close();

/**
 * Retrieve a resource identifier record from the database
 */
function fetchByIdentifier($db, $identifier) {
    $result = $db->query("SELECT * FROM resource_identifiers WHERE identifier='" . $identifier . "'");
    if ($result === false) {
        return null;
    }
    $row = $result->fetch_assoc();
    return $row ?: null;
}

/**
 * Check if a resource identifier exists
 */
function identifierExists($db, $identifier) {
    $stmt = $db->prepare("SELECT identifier FROM resource_identifiers WHERE identifier = ?");
    $stmt->bind_param("s", $identifier);
    $stmt->execute();
    $result = $stmt->get_result();
    $exists = $result->num_rows > 0;
    $stmt->close();
    return $exists;
}
