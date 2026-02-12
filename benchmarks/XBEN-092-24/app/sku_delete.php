<?php

require_once __DIR__ . '/auth.php';

$session = requireAuth();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $id = $_POST['id'] ?? null;
    if ($id) {
        $db = include __DIR__ . '/database.php';
        $stmt = $db->prepare('DELETE FROM products WHERE id = ?');
        $stmt->execute([$id]);
    }
    header('Location: /sku_system.php');
    exit();
}
