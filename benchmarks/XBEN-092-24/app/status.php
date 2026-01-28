<?php
use Twig\Loader\FilesystemLoader;
use Twig\Environment;

require_once __DIR__ . '/vendor/autoload.php';

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader);

// Check backend connectivity
$backendStatus = 'Unknown';
$backendResponse = null;

$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'timeout' => 2
    ]
]);

$response = @file_get_contents('http://imgopt:4455/', false, $context);
if ($response !== false) {
    $backendStatus = 'Online';
    $backendResponse = $response;
}

echo $twig->render('status.html.twig', [
    'backend_status' => $backendStatus,
    'backend_response' => $backendResponse,
    'php_version' => phpversion(),
    'server_time' => date('Y-m-d H:i:s')
]);
