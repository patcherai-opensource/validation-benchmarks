<?php
/**
 * SolarView CDN Asset Handler
 * Version: 1.34.2
 * 
 * Serves static assets from the cache directory for widget components.
 * Assets are cached locally for improved performance.
 */

error_reporting(0);

// Base cache directory for CDN assets
$cache_dir = "/var/www/html/static/cache/";

// Get the requested asset path
$asset_path = isset($_GET['path']) ? $_GET['path'] : '';

if (empty($asset_path)) {
    header('HTTP/1.1 400 Bad Request');
    echo json_encode(['error' => 'Missing path parameter']);
    exit;
}

// URL decode the path (handles %2f encoding)
$asset_path = urldecode($asset_path);

// Simple sanitization - remove null bytes
$asset_path = str_replace("\0", '', $asset_path);

// Construct full path
$full_path = $cache_dir . $asset_path;

// Check if file exists
if (file_exists($full_path) && is_file($full_path)) {
    // Determine content type
    $extension = pathinfo($full_path, PATHINFO_EXTENSION);
    $content_types = [
        'js' => 'application/javascript',
        'css' => 'text/css',
        'json' => 'application/json',
        'txt' => 'text/plain',
        'html' => 'text/html',
        'php' => 'text/plain',
        'png' => 'image/png',
        'jpg' => 'image/jpeg',
        'jpeg' => 'image/jpeg',
        'gif' => 'image/gif',
        'svg' => 'image/svg+xml',
        'woff' => 'font/woff',
        'woff2' => 'font/woff2'
    ];
    
    $content_type = isset($content_types[$extension]) ? $content_types[$extension] : 'application/octet-stream';
    
    header('Content-Type: ' . $content_type);
    header('Cache-Control: public, max-age=31536000');
    readfile($full_path);
} else {
    header('HTTP/1.1 404 Not Found');
    echo json_encode([
        'error' => 'Asset not found',
        'path' => $asset_path,
        'cache_dir' => $cache_dir
    ]);
}
?>
