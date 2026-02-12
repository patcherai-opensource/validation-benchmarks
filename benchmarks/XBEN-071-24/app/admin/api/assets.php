<?php
/**
 * Asset Management API
 * 
 * Provides CRUD operations for managing digital assets.
 */

require_once __DIR__ . '/../../lib/db.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

$action = $_GET['action'] ?? 'list';

try {
    $conn = \Pimcore\Db::getConnection();

    switch ($action) {
        case 'list':
            $parentId = intval($_GET['parentId'] ?? 1);
            $limit = min(intval($_GET['limit'] ?? 25), 100);
            $offset = intval($_GET['offset'] ?? 0);

            $stmt = $conn->prepare("SELECT id, parentId, type, filename, path, mimetype, creationDate, modificationDate FROM assets WHERE parentId = ? ORDER BY filename LIMIT ? OFFSET ?");
            $stmt->bind_param("iii", $parentId, $limit, $offset);
            $stmt->execute();
            $result = $stmt->get_result();
            $items = [];
            while ($row = $result->fetch_assoc()) {
                $items[] = $row;
            }
            $stmt->close();

            echo json_encode([
                'success' => true,
                'data' => $items,
                'total' => count($items)
            ]);
            break;

        case 'get':
            $id = intval($_GET['id'] ?? 0);
            if ($id <= 0) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Invalid asset ID']);
                exit;
            }

            $stmt = $conn->prepare("SELECT id, parentId, type, filename, path, mimetype, filesize, creationDate, modificationDate FROM assets WHERE id = ?");
            $stmt->bind_param("i", $id);
            $stmt->execute();
            $result = $stmt->get_result();
            $asset = $result->fetch_assoc();
            $stmt->close();

            if ($asset) {
                echo json_encode(['success' => true, 'data' => $asset]);
            } else {
                http_response_code(404);
                echo json_encode(['success' => false, 'message' => 'Asset not found']);
            }
            break;

        default:
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'Invalid action']);
            break;
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Internal server error']);
}
