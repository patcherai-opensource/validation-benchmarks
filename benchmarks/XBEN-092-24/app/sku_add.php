<?php

require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/auth.php';

$session = requireAuth();
$db = include __DIR__ . '/database.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $identifier = $_POST['identifier'] ?? '';
    $family = $_POST['family'] ?? '';
    $category_id = $_POST['category_id'] ?? null;
    $label = $_POST['label'] ?? '';
    $description = $_POST['description'] ?? '';

    if ($identifier && $label) {
        $stmt = $db->prepare('INSERT INTO products (identifier, family, category_id, label, description) VALUES (?, ?, ?, ?, ?)');
        $stmt->execute([$identifier, $family, $category_id ?: null, $label, $description]);
        header('Location: /sku_system.php');
        exit();
    }
}

$categories = $db->query('SELECT * FROM categories ORDER BY label')->fetchAll(PDO::FETCH_ASSOC);

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('product_add.html.twig', [
    'user' => $session,
    'categories' => $categories,
]);
