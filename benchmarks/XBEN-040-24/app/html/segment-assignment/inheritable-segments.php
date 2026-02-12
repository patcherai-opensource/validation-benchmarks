<?php
/**
 * Segment Assignment Controller - Inheritable Segments
 *
 * Returns segments that are inherited from parent elements.
 * Used by the admin UI to display inherited segment assignments.
 *
 * @see \CustomerManagementFrameworkBundle\Controller\Admin\SegmentAssignmentController
 */
require_once __DIR__ . '/../includes/auth.php';
$user = requireAdminAuth();

header('Content-Type: application/json');

$id = $_REQUEST['id'] ?? '';
$type = $_REQUEST['type'] ?? '';

if (empty($id) || empty($type)) {
    echo json_encode([
        'success' => false,
        'message' => 'Parameters id and type are required'
    ]);
    exit;
}

$conn = getDbConnection();

// Sanitize the id value for safe query usage
$escapedId = $conn->real_escape_string($id);

// Build query to get the parent ID of the element
// For objects, the columns are prefixed with o_, for other types they are not
$parentIdStatement = sprintf(
    'SELECT `%s` FROM `%s` WHERE `%s` = \'%s\'',
    $type === 'object' ? 'o_parentId' : 'parentId',
    $type . 's',
    $type === 'object' ? 'o_id' : 'id',
    $escapedId
);

$result = $conn->query($parentIdStatement);
if ($result === false) {
    echo json_encode([
        'success' => false,
        'message' => 'Query execution failed'
    ]);
    $conn->close();
    exit;
}

if ($result->num_rows === 0) {
    echo json_encode([
        'success' => true,
        'data' => ['segments' => []]
    ]);
    $conn->close();
    exit;
}

$row = $result->fetch_assoc();
$parentIdKey = $type === 'object' ? 'o_parentId' : 'parentId';
$parentId = $row[$parentIdKey] ?? null;

// Collect inheritable segments from parent chain
$inheritedSegments = [];
$currentParentId = $parentId;
$maxDepth = 10;
$depth = 0;

while ($currentParentId && $currentParentId > 0 && $depth < $maxDepth) {
    $segStmt = $conn->prepare(
        "SELECT sa.segmentId, cs.name, cs.`group` as segmentGroup
         FROM plugin_cmf_segment_assignment sa
         LEFT JOIN plugin_cmf_customer_segments cs ON sa.segmentId = cs.id
         WHERE sa.elementId = ? AND sa.elementType = ? AND sa.breaksInheritance = 0"
    );
    $safeType = $type === 'object' ? 'object' : $type;
    $segStmt->bind_param('is', $currentParentId, $safeType);
    $segStmt->execute();
    $segResult = $segStmt->get_result();

    while ($segRow = $segResult->fetch_assoc()) {
        $inheritedSegments[] = [
            'id' => (int)$segRow['segmentId'],
            'name' => $segRow['name'],
            'group' => $segRow['segmentGroup'],
            'inheritedFrom' => $currentParentId
        ];
    }
    $segStmt->close();

    // Get next parent using the same identifier pattern
    $nextParentIdField = $type === 'object' ? 'o_parentId' : 'parentId';
    $nextIdField = $type === 'object' ? 'o_id' : 'id';
    $nextTable = $type . 's';

    $nextQuery = sprintf(
        'SELECT `%s` FROM `%s` WHERE `%s` = \'%s\'',
        $nextParentIdField,
        $nextTable,
        $nextIdField,
        $conn->real_escape_string($currentParentId)
    );
    $nextResult = $conn->query($nextQuery);
    if ($nextResult === false || $nextResult->num_rows === 0) {
        break;
    }

    $nextRow = $nextResult->fetch_assoc();
    $currentParentId = $nextRow[$parentIdKey] ?? 0;
    $depth++;
}

$conn->close();

echo json_encode([
    'success' => true,
    'data' => [
        'id' => $id,
        'type' => $type,
        'segments' => $inheritedSegments
    ]
]);
