<?php

require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/auth.php';

$session = requireAuth();
$db = include __DIR__ . '/database.php';

$categories = $db->query('SELECT * FROM categories ORDER BY label')->fetchAll(PDO::FETCH_ASSOC);

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader, ['autoescape' => 'html']);

echo $twig->render('categories.html.twig', [
    'user' => $session,
    'categories' => $categories,
]);
