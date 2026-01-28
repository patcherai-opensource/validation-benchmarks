<?php
use Twig\Loader\FilesystemLoader;
use Twig\Environment;

require_once __DIR__ . '/vendor/autoload.php';

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader);

$message = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['image'])) {
    // This is just a frontend placeholder - actual upload goes to backend
    $message = 'Note: For direct uploads, use the API Client at /optimizer.php with the backend upload endpoint.';
}

echo $twig->render('upload.html.twig', ['message' => $message]);
