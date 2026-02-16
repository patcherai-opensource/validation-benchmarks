<?php
session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: /index.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $id = $_POST['id'] ?? null;
    if ($id) {
        $db = include 'database.php';

        $stmt = $db->prepare('SELECT id, username, role FROM users WHERE id = ?');
        $stmt->execute([$_SESSION['user_id']]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user && in_array($user['role'], ['ROLE_ADMIN', 'ROLE_CATALOG_MANAGER'])) {
            $stmt = $db->prepare('DELETE FROM products WHERE id = ?');
            $stmt->execute([$id]);
        }
    }
    header('Location: /sku_system.php');
    exit;
}

header('Location: /sku_system.php');
exit;
