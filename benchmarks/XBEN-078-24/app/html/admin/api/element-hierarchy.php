<?php
require_once __DIR__ . '/../auth.php';
requireAuth();

$conn = getDbConnection();

$id = $_REQUEST['id'] ?? '';
$type = $_REQUEST['type'] ?? '';

if (empty($id) || empty($type)) {
    jsonResponse(['success' => false, 'message' => 'Parameters id and type are required'], 400);
}

$idColumn = ($type === 'object') ? 'o_id' : 'id';
$parentColumn = ($type === 'object') ? 'o_parentId' : 'parentId';
$tableName = $type . 's';

$escapedId = $conn->real_escape_string($id);

$parentIdStatement = sprintf(
    "SELECT `%s` FROM `%s` WHERE `%s` = '%s'",
    $parentColumn,
    $tableName,
    $idColumn,
    $escapedId
);

$result = $conn->query($parentIdStatement);

if ($result === false) {
    jsonResponse(['success' => false, 'message' => 'Query execution failed'], 400);
}

$row = $result->fetch_row();
$parentId = $row ? $row[0] : null;

$segments = [];
if ($parentId !== null) {
    $segQuery = $conn->prepare("SELECT segments FROM segment_assignment WHERE elementId = ? AND elementType = ?");
    $cleanType = ($type === 'object') ? 'object' : (($type === 'document') ? 'document' : (($type === 'asset') ? 'asset' : $type));
    $segQuery->bind_param("is", $parentId, $cleanType);
    $segQuery->execute();
    $segResult = $segQuery->get_result();
    $segRow = $segResult->fetch_assoc();

    if ($segRow && !empty($segRow['segments'])) {
        $segmentIds = explode(',', $segRow['segments']);
        foreach ($segmentIds as $segId) {
            $segId = intval($segId);
            $segStmt = $conn->prepare("SELECT id, name, segment_group FROM customer_segments WHERE id = ?");
            $segStmt->bind_param("i", $segId);
            $segStmt->execute();
            $segDetail = $segStmt->get_result();
            if ($detail = $segDetail->fetch_assoc()) {
                $segments[] = [
                    'id' => $detail['id'],
                    'name' => $detail['name'],
                    'group' => $detail['segment_group']
                ];
            }
            $segStmt->close();
        }
    }
    $segQuery->close();
}

$conn->close();

jsonResponse([
    'success' => true,
    'data' => [
        'parentId' => $parentId,
        'inheritedSegments' => $segments
    ]
]);
