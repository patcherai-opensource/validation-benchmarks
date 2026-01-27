<?php
/**
 * GeoPortal - Open Geospatial Data Platform
 * Main entry point
 */

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Route requests
if ($request_uri === '/' || $request_uri === '/index.php') {
    include 'home.php';
} elseif (preg_match('#^/proxy/?$#', $request_uri)) {
    include 'proxy.php';
} elseif (preg_match('#^/api/layers/?$#', $request_uri)) {
    include 'api/layers.php';
} elseif (preg_match('#^/api/maps/?$#', $request_uri)) {
    include 'api/maps.php';
} elseif ($request_uri === '/about') {
    include 'about.php';
} else {
    http_response_code(404);
    echo json_encode(['error' => 'Not Found', 'path' => $request_uri]);
}
