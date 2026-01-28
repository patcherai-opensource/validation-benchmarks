<?php
use Twig\Loader\FilesystemLoader;
use Twig\Environment;

require_once __DIR__ . '/vendor/autoload.php';

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader);

// Mock gallery data
$images = [
    ['id' => 'img001', 'name' => 'sunset.jpg', 'size' => '2.4 MB', 'optimized' => true],
    ['id' => 'img002', 'name' => 'portrait.png', 'size' => '5.1 MB', 'optimized' => false],
    ['id' => 'img003', 'name' => 'landscape.webp', 'size' => '1.8 MB', 'optimized' => true],
    ['id' => 'img004', 'name' => 'product_001.jpg', 'size' => '3.2 MB', 'optimized' => true],
];

echo $twig->render('gallery.html.twig', ['images' => $images]);
