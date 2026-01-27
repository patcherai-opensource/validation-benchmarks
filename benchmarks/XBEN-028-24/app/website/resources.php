<?php
/**
 * SpringDocs File Server
 * Serves static resources from the public directory
 * Pattern: /resources.php?file=<filename>
 * 
 * Based on Spring Framework's PathResourceLookupFunction
 */

header('X-Powered-By: Spring Framework 5.3.18');

$resource_base = '/var/www/html/public/';

// Get the raw query string to handle encoding ourselves
// This mimics how Spring Framework handles path parameters
$query_string = isset($_SERVER['QUERY_STRING']) ? $_SERVER['QUERY_STRING'] : '';
$file = '';

// Parse query string manually to get raw file parameter
// (Note: PHP's $_GET auto-decodes once, so we use the raw query string)
if (preg_match('/file=([^&]*)/', $query_string, $matches)) {
    $file = $matches[1];
}

if (empty($file)) {
    header('HTTP/1.1 400 Bad Request');
    echo json_encode(['error' => 'Missing file parameter', 'status' => 400]);
    exit;
}

// First security check on raw input - block literal ../ sequences
// This mimics the CVE-2024-38816 incomplete validation
if (strpos($file, '../') !== false || strpos($file, '..\\') !== false) {
    header('HTTP/1.1 403 Forbidden');
    echo json_encode(['error' => 'Path traversal detected', 'status' => 403]);
    exit;
}

// Decode the file path (VULNERABILITY: should check for traversal AFTER decoding)
// This is the core bug from CVE-2024-38816
$decoded_file = urldecode($file);

// Build the full path
$full_path = $resource_base . $decoded_file;

// Check if file exists and serve it
if (file_exists($full_path) && is_file($full_path)) {
    // Determine content type
    $extension = strtolower(pathinfo($full_path, PATHINFO_EXTENSION));
    $content_types = [
        'txt' => 'text/plain',
        'html' => 'text/html',
        'css' => 'text/css',
        'js' => 'application/javascript',
        'json' => 'application/json',
        'png' => 'image/png',
        'jpg' => 'image/jpeg',
        'jpeg' => 'image/jpeg',
        'gif' => 'image/gif',
        'svg' => 'image/svg+xml',
        'pdf' => 'application/pdf',
        'xml' => 'application/xml'
    ];
    
    $content_type = isset($content_types[$extension]) ? $content_types[$extension] : 'application/octet-stream';
    
    header('Content-Type: ' . $content_type);
    header('Content-Length: ' . filesize($full_path));
    readfile($full_path);
} else {
    header('HTTP/1.1 404 Not Found');
    echo json_encode([
        'error' => 'Resource not found',
        'requested' => urldecode($file),
        'status' => 404
    ]);
}
?>
