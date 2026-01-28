<?php
require_once __DIR__ . '/vendor/autoload.php';

// Simulated archive list
$archives = [
    ['id' => 1, 'name' => 'backup_2024_01.tar', 'size' => '15.2 MB', 'created' => '2024-01-15'],
    ['id' => 2, 'name' => 'data_export.tar.gz', 'size' => '8.7 MB', 'created' => '2024-01-20'],
    ['id' => 3, 'name' => 'config_backup.zip', 'size' => '256 KB', 'created' => '2024-01-22'],
    ['id' => 4, 'name' => 'logs_archive.tar', 'size' => '42.1 MB', 'created' => '2024-01-25'],
];

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader);

echo $twig->render('archive_list.twig', ['archives' => $archives]);
