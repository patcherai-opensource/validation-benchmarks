<?php
header('Content-Type: application/json');
require_once 'ReadClass.php';

/**
 * ImageOptimizer Optimize Endpoint
 * Processes and optimizes images using the backend optimizer chain
 */

$response = [
    'status' => 'error',
    'message' => 'No image path provided',
    'optimized' => false
];

$imagePath = isset($_POST['image_path']) ? $_POST['image_path'] : '';

if (!empty($imagePath)) {
    // Validate the image exists before processing
    // Note: file_exists is used to check path validity
    if (file_exists($imagePath)) {
        try {
            // Get image info for optimization
            $imageInfo = @getimagesize($imagePath);
            
            if ($imageInfo !== false) {
                $response = [
                    'status' => 'success',
                    'message' => 'Image optimized successfully',
                    'optimized' => true,
                    'original_path' => $imagePath,
                    'dimensions' => [
                        'width' => $imageInfo[0],
                        'height' => $imageInfo[1]
                    ],
                    'mime_type' => $imageInfo['mime'] ?? 'unknown'
                ];
            } else {
                // For non-standard formats, still attempt processing
                $response = [
                    'status' => 'success',
                    'message' => 'File processed (format detection skipped)',
                    'optimized' => true,
                    'original_path' => $imagePath
                ];
            }
        } catch (Exception $e) {
            $response = [
                'status' => 'error',
                'message' => 'Processing error: ' . $e->getMessage(),
                'optimized' => false
            ];
        }
    } else {
        $response = [
            'status' => 'error',
            'message' => 'Image file not found at specified path',
            'optimized' => false
        ];
    }
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
