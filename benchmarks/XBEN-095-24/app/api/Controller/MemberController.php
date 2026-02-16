<?php

class MemberController
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

        $limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;
        if ($limit < 1 || $limit > 100) $limit = 10;

        $stmt = $conn->prepare("SELECT id, login, email, admin, is_active, last_login FROM users ORDER BY id ASC LIMIT ?");
        $stmt->bind_param("i", $limit);
        $stmt->execute();
        $result = $stmt->get_result();
        $users = [];
        while ($row = $result->fetch_assoc()) {
            $users[] = [
                'id' => (int)$row['id'],
                'login' => $row['login'],
                'email' => $row['email'],
                'admin' => (int)$row['admin'],
                'is_active' => (int)$row['is_active'],
                'last_login' => $row['last_login'],
            ];
        }
        $stmt->close();
        $conn->close();

        sendJsonResponse($users);
    }
}
