<?php
require_once __DIR__ . '/../auth.php';
requireAuth();

$conn = getDbConnection();

$id = $_GET['id'] ?? $_POST['id'] ?? '';
$type = $_GET['type'] ?? $_POST['type'] ?? '';

if (empty($id) || empty($type)) {
    jsonResponse(['success' => false, 'message' => 'Parameters id and type are required'], 400);
}

$stmt = $conn->prepare("SELECT segments, breaksInheritance FROM segment_assignment WHERE elementId = ? AND elementType = ?");
$stmt->bind_param("is", $id, $type);
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();

$segments = [];
if ($row && !empty($row['segments'])) {
    $segmentIds = explode(',', $row['segments']);
    foreach ($segmentIds as $segId) {
        $segId = intval($segId);
        $segDetail = $conn->query("SELECT id, name, segment_group FROM customer_segments WHERE id = " . $segId);
        if ($segDetail && $detail = $segDetail->fetch_assoc()) {
            $segments[] = [
                'id' => $detail['id'],
                'name' => $detail['name'],
                'group' => $detail['segment_group']
            ];
        }
    }
}

$conn->close();

jsonResponse([
    'success' => true,
    'data' => [
        'segments' => $segments,
        'breaksInheritance' => $row ? (bool)$row['breaksInheritance'] : false
    ]
]);