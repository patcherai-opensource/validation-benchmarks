<?php
/**
 * Inheritance Check API
 * 
 * Check whether an element breaks segment inheritance.
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
    "SELECT breaksInheritance FROM element_segment_assignments WHERE elementId = ? AND elementType = ?"
);
$stmt->bind_param('is', $id, $type);
$stmt->execute();
$result = $stmt->get_result();

$breaksInheritance = false;
if ($row = $result->fetch_assoc()) {
    $breaksInheritance = (bool) $row['breaksInheritance'];
}

$stmt->close();
$conn->close();

echo json_encode(['success' => true, 'breaksInheritance' => $breaksInheritance]);
