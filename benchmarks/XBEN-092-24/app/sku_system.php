<?php

require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/auth.php';

$session = requireAuth();
$db = include __DIR__ . '/database.php';

$products = $db->query('SELECT p.*, c.label as category_label FROM products p LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.updated_at DESC')->fetchAll(PDO::FETCH_ASSOC);

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('products.html.twig', [
    'user' => $session,
    'products' => $products,
]);
