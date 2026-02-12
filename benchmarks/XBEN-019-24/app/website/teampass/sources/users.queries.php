<?php
require_once __DIR__ . '/../includes/config/settings.php';
session_start();

header('Content-Type: application/json');

if (!isset($_SESSION['user_id']) || !$_SESSION['is_admin']) {
    echo json_encode(['error' => 'Insufficient privileges']);
    exit;
}

$type = isset($_POST['type']) ? $_POST['type'] : '';

switch ($type) {
    case 'list':
        echo json_encode(['users' => []]);
        break;
    default:
        echo json_encode(['error' => 'Unknown query type']);
}
