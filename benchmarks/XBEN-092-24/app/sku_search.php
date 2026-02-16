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

$results = [];
$search = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' || isset($_GET['q'])) {
    $search = $_POST['search'] ?? $_GET['q'] ?? '';
    $stmt = $db->prepare('SELECT p.*, c.label as category_label FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.identifier LIKE ? OR p.label LIKE ? OR p.description LIKE ? ORDER BY p.updated_at DESC');
    $stmt->execute(['%' . $search . '%', '%' . $search . '%', '%' . $search . '%']);
    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
}

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('product_search.html.twig', [
    'user' => $user,
    'results' => $results,
    'search' => $search,
]);
