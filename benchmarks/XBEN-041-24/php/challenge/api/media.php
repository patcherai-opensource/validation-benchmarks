<?php
header('Content-Type: application/json');

$upload_dir = '/var/www/html/upload/';
$files = [];

if (is_dir($upload_dir)) {
    $items = scandir($upload_dir);
    foreach ($items as $item) {
        if ($item !== '.' && $item !== '..' && is_file($upload_dir . $item)) {
            $files[] = [
                'name' => $item,
                'size' => filesize($upload_dir . $item),
                'modified' => date('Y-m-d H:i:s', filemtime($upload_dir . $item)),
                'url' => '/upload/' . $item
            ];
        }
    }
}

echo json_encode(['success' => true, 'files' => $files], JSON_PRETTY_PRINT);
