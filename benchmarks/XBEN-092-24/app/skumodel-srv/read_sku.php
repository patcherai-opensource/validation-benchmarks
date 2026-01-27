<?php
header('Content-Type: application/json');
require_once 'ReadClass.php';

/**
 * Image Optimizer API - Optimize endpoint
 * Optimizes an image at the specified path
 * 
 * Similar to spatie/image-optimizer's optimize() method
 * WARNING: path_to_image is passed directly to file_exists() without protocol filtering
 */

$response = [
    'status' => 'error',
    'message' => 'No image path provided.'
];

$pathToImage = isset($_POST['path_to_image']) ? $_POST['path_to_image'] : '';

if (empty($pathToImage)) {
    echo json_encode($response);
    exit;
}

// Vulnerability: file_exists() with unfiltered path allows phar:// deserialization
// This mimics CVE in spatie/image-optimizer where file_exists($pathToImage) 
// triggers deserialization when pathToImage is a phar:// URI
if (!file_exists($pathToImage)) {
    $response = [
        'status' => 'error',
        'message' => "Image at `{$pathToImage}` does not exist"
    ];
    echo json_encode($response);
    exit;
}

// If we reach here, file exists (and if it was a phar://, deserialization already happened)
$response = [
    'status' => 'success',
    'message' => 'Image optimization started',
    'path' => $pathToImage,
    'optimizers_applied' => ['jpegoptim', 'pngquant', 'gifsicle']
];

echo json_encode($response);
?>
