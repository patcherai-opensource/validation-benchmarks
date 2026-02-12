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

$error = '';

if (getSession()) {
    header('Location: /index.php');
    exit();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['_username'] ?? '';
    $password = $_POST['_password'] ?? '';

    if (authenticateUser($username, $password)) {
        header('Location: /index.php');
        exit();
    } else {
        $error = 'Invalid credentials.';
    }
}

echo $twig->render('login.html.twig', ['error' => $error]);
