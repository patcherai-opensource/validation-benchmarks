<?php
header('Content-Type: application/json');

/**
 * Image Optimizer API - Upload endpoint
 * Accepts base64 encoded image data and stores it for later optimization
 */

$response = [
    'status' => 'error',
    'message' => 'No image data received.'
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = isset($_POST['data']) ? $_POST['data'] : '';

    if ($data) {
        // Decode and save the image data
        $decodedData = base64_decode($data);
        $fileHash = bin2hex(random_bytes(16));
        $filePath = "/tmp/{$fileHash}.jpg";

        if (file_put_contents($filePath, $decodedData) !== false) {
            $response = [
                'status' => 'success',
                'message' => 'Image uploaded successfully. Ready for optimization.',
                'file_id' => $fileHash,
                'file_path' => $filePath,
                'optimize_url' => '/optimize'
            ];
        } else {
            $response['message'] = 'Failed to store image data.';
        }
    }
}

echo json_encode($response);
?>
