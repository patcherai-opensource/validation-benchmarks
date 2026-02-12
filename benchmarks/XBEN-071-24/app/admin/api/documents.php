<?php
/**
 * Document Management API
 * 
 * Provides operations for managing CMS documents.
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
            $stmt = $conn->prepare("SELECT id, parentId, type, `key`, path, published, creationDate, modificationDate FROM documents WHERE parentId = ? ORDER BY `key` LIMIT 50");
            $stmt->bind_param("i", $parentId);
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
                echo json_encode(['success' => false, 'message' => 'Invalid document ID']);
                exit;
            }

            $stmt = $conn->prepare("SELECT id, parentId, type, `key`, path, published, creationDate, modificationDate FROM documents WHERE id = ?");
            $stmt->bind_param("i", $id);
            $stmt->execute();
            $result = $stmt->get_result();
            $doc = $result->fetch_assoc();
            $stmt->close();

            if ($doc) {
                echo json_encode(['success' => true, 'data' => $doc]);
            } else {
                http_response_code(404);
                echo json_encode(['success' => false, 'message' => 'Document not found']);
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
