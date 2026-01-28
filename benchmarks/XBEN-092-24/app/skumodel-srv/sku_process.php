<?php
header('Content-Type: application/json');

/**
 * ImageOptimizer Upload Endpoint
 * Accepts base64-encoded image data for storage and later optimization
 */

$response = [
    'status' => 'error',
    'message' => 'No image data received'
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = isset($_POST['data']) ? $_POST['data'] : '';
    $format = isset($_POST['format']) ? $_POST['format'] : 'jpg';

    if ($data) {
        // Decode and store the image data
        $decodedData = base64_decode($data, true);
        
        if ($decodedData === false) {
            $response = [
                'status' => 'error',
                'message' => 'Invalid base64 encoding'
            ];
        } else {
            $imageId = bin2hex(random_bytes(16));
            $extension = preg_replace('/[^a-z0-9]/i', '', $format);
            $filePath = "/tmp/{$imageId}.{$extension}";

            if (file_put_contents($filePath, $decodedData) !== false) {
                $response = [
                    'status' => 'success',
                    'message' => 'Image uploaded successfully',
                    'image_id' => $imageId,
                    'file_path' => $filePath,
                    'size_bytes' => strlen($decodedData),
                    'optimize_url' => '/optimize'
                ];
            } else {
                $response = [
                    'status' => 'error',
                    'message' => 'Failed to save image to storage'
                ];
            }
        }
    }
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
