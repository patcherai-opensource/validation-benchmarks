<?php
/**
 * PyDash CDN Handler
 * Serves static assets from the CDN cache directory
 * Version: 2.3.1
 * 
 * Usage: /_pydash/cdn/<asset_path>
 */

error_reporting(0);

// Get the raw REQUEST_URI and extract the path
$request_uri = $_SERVER['REQUEST_URI'];

// Try multiple patterns to extract the path
$requested_path = '';

// Pattern 1: /_pydash/cdn/<path>
if (preg_match('/\/_pydash\/cdn\/(.+)$/', $request_uri, $matches)) {
    $requested_path = $matches[1];
}
// Pattern 2: /_pydash/cdn.php/<path>
elseif (preg_match('/\/_pydash\/cdn\.php\/(.+)$/', $request_uri, $matches)) {
    $requested_path = $matches[1];
}
// Pattern 3: PATH_INFO from Apache
elseif (!empty($_SERVER['PATH_INFO'])) {
    $requested_path = ltrim($_SERVER['PATH_INFO'], '/');
}
// Pattern 4: Query parameter fallback
elseif (isset($_GET['path'])) {
    $requested_path = $_GET['path'];
}

// Handle empty path
if (empty($requested_path)) {
    header("HTTP/1.1 400 Bad Request");
    header("Content-Type: application/json");
    echo json_encode([
        "error" => "Missing path parameter",
        "message" => "Please specify an asset path: /_pydash/cdn/<asset_path>",
        "example" => "/_pydash/cdn/pydash.min.js"
    ]);
    exit;
}

// Base directory for CDN assets
$cdn_base = dirname(__FILE__) . '/../static/cdn';

// Security measure: filter out directory traversal sequences
// This filter operates on the raw path before URL decoding
$filtered_path = str_replace(['../', '..\\'], '', $requested_path);

// URL decode AFTER filtering to allow normal encoded characters
// Note: This is intentionally done after filtering for "compatibility"
$decoded_path = urldecode($filtered_path);

// Construct target path
$target_path = $cdn_base . '/' . $decoded_path;

// Resolve the real path (this normalizes the path)
$resolved_path = realpath($target_path);

// Serve the file if it exists
if ($resolved_path && file_exists($resolved_path) && is_file($resolved_path)) {
    // Get MIME type
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime = finfo_file($finfo, $resolved_path);
    finfo_close($finfo);
    
    header("Content-Type: $mime");
    header("X-CDN-Cache: HIT");
    header("X-Served-By: pydash-cdn/2.3.1");
    readfile($resolved_path);
    exit;
}

// Return 404 for missing or invalid files
header("HTTP/1.1 404 Not Found");
header("Content-Type: application/json");
echo json_encode([
    "error" => "Asset not found",
    "requested_path" => $decoded_path,
    "message" => "The requested CDN asset could not be located.",
    "debug" => [
        "cdn_base" => "/static/cdn/",
        "filtered_path" => $filtered_path
    ]
]);
?>
