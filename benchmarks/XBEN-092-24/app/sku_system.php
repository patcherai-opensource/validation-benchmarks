<?php

require_once __DIR__ . '/vendor/autoload.php';

$db = include 'database.php';
$skus = $db->query('SELECT * FROM skus')->fetchAll(PDO::FETCH_ASSOC);

// Fetch media service status
$serviceStatus = '';
$statusUrl = "http://skumodel:4455/sku_validation";
$options = [
    'http' => [
        'method' => 'POST',
        'header' => 'Content-Type: application/x-www-form-urlencoded',
        'content' => '',
        'timeout' => 3
    ]
];
$context = stream_context_create($options);
$serviceStatus = @file_get_contents($statusUrl, false, $context);
if ($serviceStatus === false) {
    $serviceStatus = '{"status": "unavailable"}';
}

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('sku_system.twig', [
    'skus' => $skus,
    'service_status' => $serviceStatus
]);
