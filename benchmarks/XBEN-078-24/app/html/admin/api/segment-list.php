<?php
require_once __DIR__ . '/../auth.php';
requireAuth();

$conn = getDbConnection();

$group = $_GET['group'] ?? '';

if (!empty($group)) {
    $stmt = $conn->prepare("SELECT id, name, segment_group, reference FROM customer_segments WHERE segment_group = ? ORDER BY name ASC");
    $stmt->bind_param("s", $group);
    $stmt->execute();
    $result = $stmt->get_result();
} else {
    $result = $conn->query("SELECT id, name, segment_group, reference FROM customer_segments ORDER BY name ASC");
}

$segments = [];
while ($row = $result->fetch_assoc()) {
    $segments[] = $row;
}

$conn->close();

jsonResponse([
    'success' => true,
    'data' => $segments,
    'total' => count($segments)
]);