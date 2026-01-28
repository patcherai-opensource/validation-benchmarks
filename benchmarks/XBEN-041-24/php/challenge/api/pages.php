<?php
header('Content-Type: application/json');

$pages = [
    ['id' => 1, 'title' => 'Home', 'slug' => '/', 'status' => 'published'],
    ['id' => 2, 'title' => 'About Us', 'slug' => '/about', 'status' => 'published'],
    ['id' => 3, 'title' => 'Contact', 'slug' => '/contact', 'status' => 'published'],
    ['id' => 4, 'title' => 'Services', 'slug' => '/services', 'status' => 'draft'],
    ['id' => 5, 'title' => 'Blog', 'slug' => '/blog', 'status' => 'published']
];

echo json_encode(['success' => true, 'pages' => $pages], JSON_PRETTY_PRINT);
