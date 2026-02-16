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

$categories = $db->query('SELECT * FROM categories ORDER BY label')->fetchAll(PDO::FETCH_ASSOC);
$error = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $identifier = $_POST['identifier'] ?? '';
    $family = $_POST['family'] ?? '';
    $label = $_POST['label'] ?? '';
    $description = $_POST['description'] ?? '';
    $category_id = $_POST['category_id'] ?? null;

    if (empty($identifier) || empty($label)) {
        $error = 'Identifier and label are required fields.';
    } else {
        try {
            $stmt = $db->prepare('INSERT INTO products (identifier, family, label, description, category_id) VALUES (?, ?, ?, ?, ?)');
            $stmt->execute([$identifier, $family, $label, $description, $category_id ?: null]);
            $success = 'Product created successfully.';
        } catch (PDOException $e) {
            if (strpos($e->getMessage(), 'UNIQUE constraint') !== false) {
                $error = 'A product with this identifier already exists.';
            } else {
                $error = 'An error occurred while creating the product.';
            }
        }
    }
}

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('product_create.html.twig', [
    'user' => $user,
    'categories' => $categories,
    'error' => $error,
    'success' => $success,
]);
