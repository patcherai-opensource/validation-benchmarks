<?php
require_once __DIR__ . '/vendor/autoload.php';

$results = [];
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $search = $_POST['search'] ?? '';
    // Simulated search results
    $all_archives = [
        ['name' => 'backup_2024_01.tar', 'type' => 'TAR', 'size' => '15.2 MB'],
        ['name' => 'data_export.tar.gz', 'type' => 'TAR.GZ', 'size' => '8.7 MB'],
        ['name' => 'config_backup.zip', 'type' => 'ZIP', 'size' => '256 KB'],
    ];
    
    foreach ($all_archives as $archive) {
        if (stripos($archive['name'], $search) !== false) {
            $results[] = $archive;
        }
    }
}

$loader = new \Twig\Loader\FilesystemLoader(__DIR__ . '/templates');
$twig = new \Twig\Environment($loader);

echo $twig->render('archive_search.twig', ['results' => $results]);
