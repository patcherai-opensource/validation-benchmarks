<?php

use Twig\Loader\FilesystemLoader;
use Twig\Environment;

require_once __DIR__ . '/vendor/autoload.php';

$username = isset($_POST['username']) ? htmlspecialchars($_POST['username']) : 'anonymous';

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader, [
    'autoescape' => 'html',
]);

try {
    echo $twig->render('hello.html.twig', ['username' => $username]);
} catch (\Exception $e) {
    http_response_code(500);
    echo 'An error occurred.';
}
