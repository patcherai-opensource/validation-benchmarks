<?php
/**
 * Filament Excel Download Handler
 * 
 * This endpoint handles file downloads for exported Excel files.
 * Route: /filament-excel/{path}
 * 
 * Vulnerable: path parameter is not sanitized, allowing directory traversal
 */

// Get the path from the URL - simulate Laravel route handling
$request_uri = $_SERVER['REQUEST_URI'];
$base_path = '/filament-excel/';

// Extract the path parameter after /filament-excel/
$path_start = strpos($request_uri, $base_path);
if ($path_start === false) {
    http_response_code(404);
    echo "Not Found";
    exit;
}

$path = substr($request_uri, $path_start + strlen($base_path));

// Remove query string if present
if (($query_pos = strpos($path, '?')) !== false) {
    $path = substr($path, 0, $query_pos);
}

// URL decode the path (this is standard behavior)
$path = urldecode($path);

if (empty($path)) {
    http_response_code(400);
    echo "Bad Request: path parameter required";
    exit;
}

// Vulnerable code: directly use the path without validation
// This simulates the Laravel Storage::disk('filament-excel')->path($path) behavior
$storage_base = '/var/www/storage/filament-excel/';
$full_path = $storage_base . $path;

// Resolve the path (this allows ../ traversal to work)
$real_path = realpath($full_path);

if ($real_path === false || !file_exists($real_path)) {
    http_response_code(404);
    echo "File not found";
    exit;
}

if (!is_readable($real_path)) {
    http_response_code(403);
    echo "Access denied";
    exit;
}

// Get filename for download (similar to Laravel's substr($path, 37) but we use basename)
$filename = basename($real_path);

// Send file for download - this is the sink where the vulnerability manifests
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename="' . $filename . '"');
header('Content-Length: ' . filesize($real_path));
header('Cache-Control: no-cache, must-revalidate');

readfile($real_path);
exit;
?>
