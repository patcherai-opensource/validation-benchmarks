<?php

require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/auth.php';

$session = requireAuth();
$db = include __DIR__ . '/database.php';

$id = $_GET['id'] ?? null;
$product = null;
if ($id) {
    $stmt = $db->prepare('SELECT p.*, c.label as category_label FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.id = ?');
    $stmt->execute([$id]);
    $product = $stmt->fetch(PDO::FETCH_ASSOC);
}

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('product_detail.html.twig', [
    'user' => $session,
    'product' => $product,
]);
