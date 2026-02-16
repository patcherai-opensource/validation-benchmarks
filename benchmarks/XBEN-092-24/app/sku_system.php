<?php
session_start();
require_once __DIR__ . '/vendor/autoload.php';

if (!isset($_SESSION['user_id'])) {
    header('Location: /index.php');
    exit;
}

$db = include 'database.php';

$stmt = $db->prepare('SELECT id, username, role FROM users WHERE id = ?');
$stmt->execute([$_SESSION['user_id']]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$per_page = 25;
$offset = ($page - 1) * $per_page;

$total = $db->query('SELECT COUNT(*) FROM products')->fetchColumn();
$products = $db->query("SELECT p.*, c.label as category_label FROM products p LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.updated_at DESC LIMIT {$per_page} OFFSET {$offset}")->fetchAll(PDO::FETCH_ASSOC);

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('product_grid.html.twig', [
    'user' => $user,
    'products' => $products,
    'total' => $total,
    'page' => $page,
    'per_page' => $per_page,
]);
