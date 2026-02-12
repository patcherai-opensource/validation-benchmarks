<?php
/**
 * UUID Resolver API
 * 
 * Resolves UUIDs to their associated objects/resources.
 * Used internally by the admin panel and external integrations.
 */

require_once __DIR__ . '/../../lib/db.php';
require_once __DIR__ . '/../../models/Tool/UUID/Dao.php';
require_once __DIR__ . '/../../models/Tool/UUID.php';

header('Content-Type: application/json');

// Only allow GET requests
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

$action = $_GET['action'] ?? '';

switch ($action) {
    case 'get':
        $uuid = $_GET['uuid'] ?? '';
        
        if (empty($uuid)) {
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'UUID parameter is required']);
            exit;
        }
        
        try {
            $uuidModel = \Pimcore\Model\Tool\UUID::getByUuid($uuid);
            if ($uuidModel) {
                echo json_encode([
                    'success' => true,
                    'data' => $uuidModel
                ]);
            } else {
                http_response_code(404);
                echo json_encode(['success' => false, 'message' => 'UUID not found']);
            }
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => 'Internal server error']);
        }
        break;
    
    case 'exists':
        $uuid = $_GET['uuid'] ?? '';
        
        if (empty($uuid)) {
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'UUID parameter is required']);
            exit;
        }
        
        try {
            $dao = new \Pimcore\Model\Tool\UUID\Dao();
            $exists = $dao->exists($uuid);
            echo json_encode([
                'success' => true,
                'exists' => $exists
            ]);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => 'Internal server error']);
        }
        break;
    
    case 'list':
        try {
            $conn = \Pimcore\Db::getConnection();
            $result = $conn->query("SELECT uuid, itemId, type FROM uuids ORDER BY itemId LIMIT 50");
            $items = [];
            while ($row = $result->fetch_assoc()) {
                $items[] = $row;
            }
            echo json_encode([
                'success' => true,
                'data' => $items,
                'total' => count($items)
            ]);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => 'Internal server error']);
        }
        break;
    
    default:
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'message' => 'Invalid action. Supported actions: get, exists, list'
        ]);
        break;
}
