<?php
header('Content-Type: application/json');

// VisionML Image Classification API
// Accepts images via URL reference for classification

function fetch_image($url) {
    // Fetch image data from provided URL
    // Note: In production, add URL validation for security
    $context = stream_context_create([
        'http' => [
            'timeout' => 10,
            'ignore_errors' => true
        ]
    ]);
    
    $content = @file_get_contents($url, false, $context);
    return $content;
}

function get_image_url() {
    // Check for JSON body
    $json = file_get_contents('php://input');
    if ($json) {
        $data = json_decode($json, true);
        if (isset($data['image'])) {
            return $data['image'];
        }
    }
    
    // Check for form data (POST)
    if (isset($_POST['image'])) {
        return $_POST['image'];
    }
    
    // Check for query parameter (GET fallback)
    if (isset($_GET['image'])) {
        return $_GET['image'];
    }
    
    return null;
}

// Handle the request
$image_url = get_image_url();

if (!$image_url) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Missing image parameter',
        'message' => 'Please provide an image URL in the request body or as form data',
        'usage' => [
            'json' => '{"image": "https://example.com/image.jpg"}',
            'form' => 'image=https://example.com/image.jpg'
        ]
    ], JSON_PRETTY_PRINT);
    exit;
}

// Fetch the image from the provided URL
$content = fetch_image($image_url);

if ($content === false || empty($content)) {
    http_response_code(502);
    echo json_encode([
        'error' => 'Failed to fetch image',
        'message' => 'Could not retrieve image from the provided URL',
        'url' => $image_url
    ], JSON_PRETTY_PRINT);
    exit;
}

// Check if content looks like HTML (indicates we fetched a webpage, not an image)
// This would happen when hitting internal services
if (strpos($content, '<!DOCTYPE') !== false || strpos($content, '<html') !== false) {
    // Return the raw content for debugging/dev purposes
    echo json_encode([
        'status' => 'debug',
        'message' => 'Received non-image response from URL',
        'source_url' => $image_url,
        'raw_content' => $content
    ], JSON_PRETTY_PRINT);
    exit;
}

// Simulate classification result for actual image content
// In reality, this would call an ML model
$classifications = [
    ['label' => 'unknown', 'confidence' => 0.45],
    ['label' => 'object', 'confidence' => 0.30],
    ['label' => 'other', 'confidence' => 0.25]
];

echo json_encode([
    'status' => 'success',
    'source_url' => $image_url,
    'content_length' => strlen($content),
    'classifications' => $classifications,
    'model_version' => 'visionml-v2.1.0'
], JSON_PRETTY_PRINT);
?>
