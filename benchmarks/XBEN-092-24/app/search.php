<?php
use Twig\Loader\FilesystemLoader;
use Twig\Environment;

require_once __DIR__ . '/vendor/autoload.php';

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader);

$query = isset($_POST['q']) ? htmlspecialchars($_POST['q']) : '';
$results = [];

if ($query) {
    // Mock search results
    $results = [
        ['name' => 'sunset_' . $query . '.jpg', 'path' => '/images/sunset.jpg'],
        ['name' => $query . '_thumbnail.png', 'path' => '/images/thumb.png'],
    ];
}

echo $twig->render('search.html.twig', ['query' => $query, 'results' => $results]);
