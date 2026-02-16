<?php
/**
 * Element Hierarchy API
 * 
 * Retrieves parent hierarchy and inherited segment assignments
 * for CMS elements (documents, assets, objects).
 * 
 * Parameters:
 *   id   - Element ID
 *   type - Element type (document, asset, object)
 */
require_once __DIR__ . '/../auth.php';
requireAdmin();

header('Content-Type: application/json');

$id = isset($_REQUEST['id']) ? $_REQUEST['id'] : '';
$type = isset($_REQUEST['type']) ? $_REQUEST['type'] : '';

if (empty($id) || empty($type)) {
    echo json_encode(['success' => false, 'message' => 'Missing required parameters']);
    exit;
}

$conn = getDbConnection();

// Sanitize the id value for safe use in queries
$safeId = $conn->real_escape_string($id);

// Determine the correct column names and table based on element type
// Objects use o_ prefixed columns, other types use standard names
if ($type === 'object') {
    $parentColumn = 'o_parentId';
    $idColumn = 'o_id';
} else {
    $parentColumn = 'parentId';
    $idColumn = 'id';
}

$tableName = $type . 's';

// Build query to find parent element
$parentQuery = sprintf(
    "SELECT `%s` FROM `%s` WHERE `%s` = '%s'",
    $parentColumn,
    $tableName,
    $idColumn,
    $safeId
);

$parentResult = $conn->query($parentQuery);

if ($parentResult === false) {
    echo json_encode(['success' => false, 'message' => 'Query preparation failed']);
    $conn->close();
    exit;
}

if ($parentResult->num_rows === 0) {
    echo json_encode(['success' => true, 'data' => [], 'parentId' => null]);
    $conn->close();
    exit;
}

$parentRow = $parentResult->fetch_assoc();
$parentId = reset($parentRow);

// Get inherited segments from parent
$segStmt = $conn->prepare(
    "SELECT s.id, s.name, s.type FROM element_segment_index esi 
     JOIN customer_segments s ON esi.segmentId = s.id 
     WHERE esi.elementId = ? AND esi.elementType = ?"
);
$segStmt->bind_param('is', $parentId, $type);
$segStmt->execute();
$segResult = $segStmt->get_result();

$segments = [];
while ($row = $segResult->fetch_assoc()) {
    $segments[] = $row;
}
$segStmt->close();
$conn->close();

echo json_encode([
    'success' => true,
    'data' => $segments,
    'parentId' => $parentId
]);
