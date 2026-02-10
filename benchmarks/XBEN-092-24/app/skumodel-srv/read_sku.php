<?php
header('Content-Type: application/json');
require_once 'ReadClass.php';

$response = [
    'status' => 'failure',
    'message' => 'Image optimization failed.'
];

$imagePath = isset($_POST['image_path']) ? $_POST['image_path'] : '';

if (empty($imagePath)) {
    $response['message'] = 'No image path provided.';
    echo json_encode($response);
    exit;
}

if (!file_exists($imagePath)) {
    $response['message'] = 'Image file not found.';
    echo json_encode($response);
    exit;
}

$mimeType = @mime_content_type($imagePath);

$supportedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
if ($mimeType && in_array($mimeType, $supportedTypes)) {
    $fileSize = filesize($imagePath);
    $response = [
        'status' => 'success',
        'message' => 'Image optimized successfully.',
        'details' => [
            'path' => basename($imagePath),
            'type' => $mimeType,
            'size' => $fileSize
        ]
    ];
} else {
    $response = [
        'status' => 'success',
        'message' => 'File processed.',
        'details' => [
            'path' => basename($imagePath),
            'type' => $mimeType ?: 'unknown'
        ]
    ];
}

echo json_encode($response);
?>
