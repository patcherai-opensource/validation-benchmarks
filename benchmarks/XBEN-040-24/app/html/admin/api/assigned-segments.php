<?php
/**
 * Assigned Segments API
 * 
 * Returns directly assigned segments for a given element.
 */
require_once __DIR__ . '/../auth.php';
requireAdmin();

header('Content-Type: application/json');

$id = isset($_REQUEST['id']) ? intval($_REQUEST['id']) : 0;
$type = isset($_REQUEST['type']) ? $_REQUEST['type'] : '';

$allowedTypes = ['document', 'asset', 'object'];
if (!in_array($type, $allowedTypes) || $id <= 0) {
    echo json_encode(['success' => false, 'message' => 'Invalid parameters']);
    exit;
}

$conn = getDbConnection();

$stmt = $conn->prepare(
    "SELECT esa.segments, esa.breaksInheritance 
     FROM element_segment_assignments esa 
     WHERE esa.elementId = ? AND esa.elementType = ?"
);
$stmt->bind_param('is', $id, $type);
$stmt->execute();
$result = $stmt->get_result();

$data = [];
if ($row = $result->fetch_assoc()) {
    $segmentIds = array_filter(explode(',', $row['segments']));
    foreach ($segmentIds as $sid) {
        $segStmt = $conn->prepare("SELECT id, name, type FROM customer_segments WHERE id = ?");
        $segStmt->bind_param('i', $sid);
        $segStmt->execute();
        $segResult = $segStmt->get_result();
        if ($seg = $segResult->fetch_assoc()) {
            $data[] = $seg;
        }
        $segStmt->close();
    }
}

$stmt->close();
$conn->close();

echo json_encode(['success' => true, 'data' => $data]);
