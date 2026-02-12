<?php

require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/auth.php';

use Twig\Loader\FilesystemLoader;
use Twig\Environment;

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader, [
    'charset' => 'UTF-8',
    'strict_variables' => false,
    'autoescape' => 'html',
]);

$session = getSession();

if (!$session) {
    header('Location: /login.php');
    exit();
}

$db = include __DIR__ . '/database.php';

$recentProducts = $db->query('SELECT * FROM products ORDER BY updated_at DESC LIMIT 10')->fetchAll(PDO::FETCH_ASSOC);
$categoryCount = $db->query('SELECT COUNT(*) FROM categories')->fetchColumn();
$productCount = $db->query('SELECT COUNT(*) FROM products')->fetchColumn();

echo $twig->render('dashboard.html.twig', [
    'user' => $session,
    'recent_products' => $recentProducts,
    'category_count' => $categoryCount,
    'product_count' => $productCount,
]);
