<?php
header('Content-Type: application/json');

$response = [
    'status' => 'success',
    'statistics' => [
        'images_processed' => rand(1000, 50000),
        'total_size_saved_mb' => rand(100, 5000),
        'average_compression_ratio' => round(rand(60, 85) / 100, 2),
        'supported_formats' => ['jpeg', 'png', 'gif', 'webp', 'avif'],
        'max_file_size_mb' => 50
    ],
    'optimizer_chain' => [
        'jpegoptim' => '1.4.6',
        'optipng' => '0.7.7',
        'pngquant' => '2.12.5',
        'svgo' => '2.8.0',
        'gifsicle' => '1.92'
    ],
    'timestamp' => date('Y-m-d H:i:s')
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
