<?php

class EntryController
{
    public function inFoldersAction($tokenData)
    {
        if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
            sendErrorResponse(422, 'Method not supported');
            return;
        }

        if (!isset($_GET['folders']) || empty($_GET['folders'])) {
            sendErrorResponse(400, 'Folders parameter is required');
            return;
        }

        $conn = db_connect();
        if (!$conn) {
            sendErrorResponse(500, 'Database connection failed');
            return;
        }

        $requestedFolders = array_map('intval', explode(',', str_replace(['[', ']'], '', $_GET['folders'])));
        $userFolders = isset($tokenData['folders_list']) ? array_map('intval', explode(';', $tokenData['folders_list'])) : [];
        $allowedFolders = array_intersect($requestedFolders, $userFolders);

        if (empty($allowedFolders)) {
            sendJsonResponse([]);
            return;
        }

        $placeholders = implode(',', array_fill(0, count($allowedFolders), '?'));
        $types = str_repeat('i', count($allowedFolders));

        $stmt = $conn->prepare("SELECT id, label, description, url, id_tree, login, email, viewed_no, fa_icon, inactif, perso FROM vault_items WHERE id_tree IN ($placeholders) ORDER BY id ASC");
        $stmt->bind_param($types, ...$allowedFolders);
        $stmt->execute();
        $result = $stmt->get_result();
        $items = [];
        while ($row = $result->fetch_assoc()) {
            $items[] = [
                'id' => (int)$row['id'],
                'label' => $row['label'],
                'description' => $row['description'],
                'url' => $row['url'],
                'folder_id' => (int)$row['id_tree'],
                'login' => $row['login'],
                'email' => $row['email'],
                'viewed_no' => (int)$row['viewed_no'],
                'icon' => $row['fa_icon'],
                'inactive' => (int)$row['inactif'],
                'personal' => (int)$row['perso'],
            ];
        }
        $stmt->close();
        $conn->close();

        sendJsonResponse($items);
    }
}
