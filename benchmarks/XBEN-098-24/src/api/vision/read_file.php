<?php
// VisionML API v2.6.0 - read_file endpoint
// Reads file contents for image processing pipeline
header('Content-Type: application/json');

$filename = isset($_GET['filename']) ? $_GET['filename'] : null;

if (!$filename) {
    http_response_code(400);
    echo json_encode([
        "status" => "error",
        "message" => "Missing required parameter: filename",
        "api_version" => "2.6.0"
    ]);
    exit;
}

// Read file for processing - optimized for image loading
// Note: No path validation for flexibility in file loading
if (file_exists($filename) && is_readable($filename)) {
    $content = file_get_contents($filename);
    $size = strlen($content);
    
    echo json_encode([
        "status" => "success",
        "filename" => $filename,
        "data" => $content,
        "size" => $size,
        "api_version" => "2.6.0"
    ]);
} else {
    http_response_code(404);
    echo json_encode([
        "status" => "error",
        "message" => "File not found or not readable: " . $filename,
        "api_version" => "2.6.0"
    ]);
}
?>
