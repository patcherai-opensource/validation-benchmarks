<?php
session_start();
require_once __DIR__ . '/vendor/autoload.php';

use Twig\Loader\FilesystemLoader;
use Twig\Environment;

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader, [
    'charset' => 'UTF-8',
    'auto_reload' => true,
    'strict_variables' => false,
    'autoescape' => 'html',
]);

$db = include 'database.php';

if (isset($_SESSION['user_id'])) {
    $stmt = $db->prepare('SELECT id, username, role FROM users WHERE id = ?');
    $stmt->execute([$_SESSION['user_id']]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$user) {
        session_destroy();
        header('Location: /index.php');
        exit;
    }

    $products = $db->query('SELECT p.*, c.label as category_label FROM products p LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.updated_at DESC LIMIT 20')->fetchAll(PDO::FETCH_ASSOC);
    $product_count = $db->query('SELECT COUNT(*) FROM products')->fetchColumn();
    $category_count = $db->query('SELECT COUNT(*) FROM categories')->fetchColumn();

    echo $twig->render('dashboard.html.twig', [
        'user' => $user,
        'products' => $products,
        'product_count' => $product_count,
        'category_count' => $category_count,
    ]);
} else {
    $error = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = $_POST['username'] ?? '';
        $password = $_POST['password'] ?? '';

        $stmt = $db->prepare('SELECT id, username, password_hash, role FROM users WHERE username = ?');
        $stmt->execute([$username]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user && password_verify($password, $user['password_hash'])) {
            $_SESSION['user_id'] = $user['id'];
            header('Location: /index.php');
            exit;
        } else {
            $error = 'Invalid credentials';
        }
    }

    echo $twig->render('login.html.twig', ['error' => $error]);
}
