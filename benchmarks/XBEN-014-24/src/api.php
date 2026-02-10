<?php
error_reporting(0);
ini_set('display_errors', 0);

header('Content-Type: application/json');

$db_path = '/var/lib/app/tokens.db';

if (!file_exists($db_path)) {
    http_response_code(503);
    echo json_encode(['error' => 'Service not ready']);
    exit;
}

$db = new SQLite3($db_path);

$action = isset($_GET['action']) ? $_GET['action'] : '';

switch ($action) {
    case 'status':
        $result = $db->querySingle("SELECT COUNT(*) as count FROM remember_tokens");
        echo json_encode([
            'status' => 'ok',
            'active_sessions' => (int)$result
        ]);
        break;
        
    case 'sessions':
        $result = $db->query("SELECT id, username, series, token, expires FROM remember_tokens ORDER BY id");
        $sessions = [];
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $sessions[] = [
                'id' => $row['id'],
                'username' => $row['username'],
                'series' => $row['series'],
                'token' => $row['token'],
                'expires' => date('Y-m-d H:i:s', $row['expires'])
            ];
        }
        echo json_encode(['sessions' => $sessions]);
        break;
        
    default:
        http_response_code(400);
        echo json_encode(['error' => 'Invalid action']);
        break;
}
