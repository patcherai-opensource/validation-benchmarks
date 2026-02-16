<?php

class CategoryController
{
    public function listAction($tokenData)
    {
        if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
            sendErrorResponse(422, 'Method not supported');
            return;
        }

        $conn = db_connect();
        if (!$conn) {
            sendErrorResponse(500, 'Database connection failed');
            return;
        }

        $stmt = $conn->prepare("SELECT id, parent_id, title, personal_folder FROM vault_folders ORDER BY parent_id, title");
        $stmt->execute();
        $result = $stmt->get_result();
        $folders = [];
        while ($row = $result->fetch_assoc()) {
            $folders[] = [
                'id' => (int)$row['id'],
                'parent_id' => (int)$row['parent_id'],
                'title' => $row['title'],
                'personal_folder' => (int)$row['personal_folder'],
            ];
        }
        $stmt->close();
        $conn->close();

        sendJsonResponse($folders);
    }
}
