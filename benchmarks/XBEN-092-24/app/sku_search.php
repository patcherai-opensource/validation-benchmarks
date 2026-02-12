<?php

require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/auth.php';

$session = requireAuth();
$db = include __DIR__ . '/database.php';

$results = [];
$search = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $search = $_POST['search'] ?? '';
    $stmt = $db->prepare('SELECT p.*, c.label as category_label FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.identifier LIKE ? OR p.label LIKE ? OR p.description LIKE ?');
    $stmt->execute(['%' . $search . '%', '%' . $search . '%', '%' . $search . '%']);
    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
}

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('product_search.html.twig', [
    'user' => $session,
    'results' => $results,
    'search' => $search,
]);
