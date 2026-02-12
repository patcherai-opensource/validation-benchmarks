<?php
require_once __DIR__ . '/../includes/config/settings.php';
session_start();

header('Content-Type: application/json');

if (!isset($_SESSION['user_id'])) {
    echo json_encode(['error' => 'Not authenticated']);
    exit;
}

$type = isset($_POST['type']) ? $_POST['type'] : '';

switch ($type) {
    case 'show_details':
        $itemId = isset($_POST['id']) ? intval($_POST['id']) : 0;
        echo json_encode(['item' => null, 'error' => 'Item not found']);
        break;
    case 'create':
        echo json_encode(['error' => 'Not implemented']);
        break;
    default:
        echo json_encode(['error' => 'Unknown query type']);
}
