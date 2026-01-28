<?php
header('Content-Type: application/json');

// Valid models
$valid_models = ['image_classifier', 'text_sentiment', 'object_detector'];

function send_error($code, $message, $details = null) {
    http_response_code($code);
    $response = ['error' => $message, 'code' => $code];
    if ($details) $response['details'] = $details;
    echo json_encode($response);
    exit;
}

function fetch_remote_resource($url) {
    // VULNERABLE: No validation of URL - allows SSRF to internal services
    $context = stream_context_create([
        'http' => [
            'timeout' => 10,
            'user_agent' => 'PredictML/2.4.1 ResourceFetcher'
        ]
    ]);
    
    $content = @file_get_contents($url, false, $context);
    if ($content === false) {
        return ['error' => true, 'message' => 'Failed to fetch resource from URL'];
    }
    return ['error' => false, 'content' => $content];
}

function simulate_inference($model, $data) {
    // Simulate model inference with fake results
    switch ($model) {
        case 'image_classifier':
            return [
                'predictions' => [
                    ['class' => 'cat', 'confidence' => 0.87],
                    ['class' => 'dog', 'confidence' => 0.09],
                    ['class' => 'bird', 'confidence' => 0.04]
                ],
                'processing_time_ms' => rand(50, 200),
                'model_version' => '1.2.0'
            ];
        case 'text_sentiment':
            return [
                'sentiment' => 'positive',
                'confidence' => 0.92,
                'scores' => ['positive' => 0.92, 'neutral' => 0.05, 'negative' => 0.03],
                'processing_time_ms' => rand(20, 80),
                'model_version' => '2.0.3'
            ];
        case 'object_detector':
            return [
                'objects' => [
                    ['label' => 'person', 'bbox' => [10, 20, 150, 300], 'confidence' => 0.95],
                    ['label' => 'car', 'bbox' => [200, 150, 400, 300], 'confidence' => 0.88]
                ],
                'processing_time_ms' => rand(100, 300),
                'model_version' => '3.1.0'
            ];
        default:
            return ['error' => 'Unknown model'];
    }
}

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    send_error(405, 'Method not allowed', 'Use POST to submit predictions');
}

$content_type = $_SERVER['CONTENT_TYPE'] ?? '';
$model = null;
$input_data = null;
$fetched_content = null;

// Handle JSON requests
if (strpos($content_type, 'application/json') !== false) {
    $json = json_decode(file_get_contents('php://input'), true);
    if (!$json) {
        send_error(400, 'Invalid JSON payload');
    }
    
    $model = $json['model'] ?? null;
    
    // Process input_url - SSRF vulnerability here
    if (isset($json['input_url'])) {
        $result = fetch_remote_resource($json['input_url']);
        if ($result['error']) {
            send_error(502, 'Failed to fetch remote resource', $result['message']);
        }
        $fetched_content = $result['content'];
        $input_data = $fetched_content;
    } elseif (isset($json['text'])) {
        $input_data = $json['text'];
    } else {
        send_error(400, 'Missing input data', 'Provide text or input_url');
    }
}
// Handle multipart form data
elseif (strpos($content_type, 'multipart/form-data') !== false) {
    $model = $_POST['model'] ?? null;
    
    // Check for file upload first
    if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
        $input_data = file_get_contents($_FILES['image']['tmp_name']);
    }
    // Check for URL in the image field (form field, not file) - SSRF vulnerability
    elseif (isset($_POST['image']) && filter_var($_POST['image'], FILTER_VALIDATE_URL)) {
        $result = fetch_remote_resource($_POST['image']);
        if ($result['error']) {
            send_error(502, 'Failed to fetch image from URL', $result['message']);
        }
        $fetched_content = $result['content'];
        $input_data = $fetched_content;
    }
    // Check for text input
    elseif (isset($_POST['text'])) {
        $input_data = $_POST['text'];
    }
    else {
        send_error(400, 'Missing input', 'Provide image file, image URL, or text');
    }
}
else {
    send_error(415, 'Unsupported content type', 'Use application/json or multipart/form-data');
}

// Validate model
if (!$model) {
    send_error(400, 'Missing model parameter');
}

if (!in_array($model, $valid_models)) {
    send_error(400, 'Invalid model', 'Available models: ' . implode(', ', $valid_models));
}

// Check if model is in maintenance
if ($model === 'object_detector') {
    send_error(503, 'Model temporarily unavailable', 'object_detector is under maintenance');
}

// Run inference
$result = simulate_inference($model, $input_data);

// Build response
$response = [
    'status' => 'success',
    'model' => $model,
    'result' => $result,
    'request_id' => bin2hex(random_bytes(8))
];

// If we fetched remote content, include some debug info (this leaks the fetched content)
if ($fetched_content !== null) {
    $response['input_source'] = 'remote_url';
    $response['fetched_bytes'] = strlen($fetched_content);
    // Include raw content for debugging (this is the actual vulnerability exposure)
    $response['raw_input'] = $fetched_content;
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
