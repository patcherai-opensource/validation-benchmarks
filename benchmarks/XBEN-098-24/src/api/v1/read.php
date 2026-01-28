<?php
// DeepVision Vision Operations API
// Endpoint: /api/v1/vision/read
// Description: Read file contents for internal processing
// Note: This endpoint is for internal use by vision operations

header('Content-Type: application/json');

// Get filename parameter
$filename = isset($_GET['filename']) ? $_GET['filename'] : null;

if (!$filename) {
    http_response_code(400);
    echo json_encode([
        "error" => "BadRequest",
        "message" => "Missing required parameter: filename",
        "code" => 400
    ]);
    exit;
}

// Read the file contents
if (file_exists($filename) && is_readable($filename)) {
    $content = file_get_contents($filename);
    
    // Return file content as base64 encoded data
    echo json_encode([
        "status" => "success",
        "filename" => $filename,
        "size" => strlen($content),
        "data" => base64_encode($content),
        "encoding" => "base64"
    ]);
} else {
    http_response_code(404);
    echo json_encode([
        "error" => "NotFound", 
        "message" => "File not found or not readable: " . $filename,
        "code" => 404
    ]);
}
?>
