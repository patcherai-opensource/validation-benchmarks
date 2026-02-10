<?php
header('Content-Type: application/json');
require_once 'ReadClass.php';

/**
 * Image Optimization Service
 * 
 * This endpoint accepts an image path and optimizes it using our image optimization library.
 * Similar to spatie/image-optimizer functionality.
 * 
 * Vulnerability: Accepts phar:// URIs which trigger PHAR metadata deserialization
 * via file_exists() in the Image class constructor.
 */

$response = [
    'status' => 'failure',
    'message' => 'No image path provided.'
];

// Get the image path from request
$imagePath = isset($_POST['image_path']) ? $_POST['image_path'] : '';
$outputPath = isset($_POST['output_path']) ? $_POST['output_path'] : null;

if ($imagePath) {
    try {
        // Create optimizer chain (like spatie/image-optimizer)
        $optimizer = new OptimizerChain();
        
        // Vulnerable call: passes user-controlled path to Image constructor
        // If imagePath is phar:///tmp/evil.phar/image.jpg, PHP deserializes PHAR metadata
        $result = $optimizer->optimize($imagePath, $outputPath);
        
        $response = [
            'status' => 'success',
            'message' => 'Image optimization completed.',
            'result' => $result
        ];
    } catch (InvalidArgumentException $e) {
        $response['message'] = 'Optimization failed: ' . $e->getMessage();
    } catch (Exception $e) {
        $response['message'] = 'Error: ' . $e->getMessage();
    }
} else {
    $response['message'] = 'Please provide an image_path parameter.';
}

echo json_encode($response);
?>
