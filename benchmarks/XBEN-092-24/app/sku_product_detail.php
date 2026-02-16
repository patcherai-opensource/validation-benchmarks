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

$id = isset($_GET['id']) ? (int)$_GET['id'] : null;
$product = null;
$media = [];

if ($id) {
    $stmt = $db->prepare('SELECT p.*, c.label as category_label FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.id = ?');
    $stmt->execute([$id]);
    $product = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($product) {
        $stmt = $db->prepare('SELECT * FROM product_media WHERE product_id = ? ORDER BY uploaded_at DESC');
        $stmt->execute([$id]);
        $media = $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('product_detail.html.twig', [
    'user' => $user,
    'product' => $product,
    'media' => $media,
]);
