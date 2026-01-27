<?php
/**
 * GeoPortal Proxy Service
 * 
 * Provides proxy functionality for fetching external geospatial resources.
 * Uses host whitelisting for security.
 */

header('Content-Type: application/json');

// Allowed hosts for proxying - whitelisted domains
$PROXY_ALLOWED_HOSTS = [
    'openstreetmap.org',
    'tile.openstreetmap.org',
    'api.openstreetmap.org', 
    'nominatim.openstreetmap.org',
    'geoserver.org',
    'maps.googleapis.com',
    'api.mapbox.com',
    'tiles.mapbox.com',
    'example.com',
    'geoportal.local',
    'localhost'
];

// Blocked internal paths - security measure
$BLOCKED_PATHS = [
    '/metadata.txt',
    '/secrets',
    '/admin',
    '/internal'
];

/**
 * Validate if host is in whitelist
 */
function validate_host($hostname, $allowed_hosts) {
    if (empty($hostname)) {
        return false;
    }
    
    // Normalize hostname to lowercase
    $hostname = strtolower($hostname);
    
    foreach ($allowed_hosts as $allowed) {
        if ($hostname === $allowed || str_ends_with($hostname, '.' . $allowed)) {
            return true;
        }
    }
    return false;
}

/**
 * Check if path is blocked
 */
function is_path_blocked($path, $blocked_paths) {
    if (empty($path)) {
        return false;
    }
    
    // Normalize path to lowercase for comparison
    $path_lower = strtolower($path);
    
    foreach ($blocked_paths as $blocked) {
        if (strpos($path_lower, strtolower($blocked)) !== false) {
            return true;
        }
    }
    return false;
}

// Check if URL parameter is provided
if (!isset($_GET['url']) || empty($_GET['url'])) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Missing required parameter',
        'message' => 'The url parameter is required. Usage: /proxy/?url=<external_url>',
        'allowed_hosts' => $PROXY_ALLOWED_HOSTS
    ]);
    exit;
}

$raw_url = $_GET['url'];

// Parse and validate the URL
$parsed = parse_url($raw_url);

if ($parsed === false || !isset($parsed['host'])) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Invalid URL',
        'message' => 'Could not parse the provided URL',
        'url' => $raw_url
    ]);
    exit;
}

$hostname = $parsed['host'];
$path = isset($parsed['path']) ? $parsed['path'] : '/';

// Validate host against whitelist
if (!validate_host($hostname, $PROXY_ALLOWED_HOSTS)) {
    http_response_code(403);
    echo json_encode([
        'error' => 'Host not allowed',
        'message' => "The host '$hostname' is not in the allowed hosts list",
        'allowed_hosts' => $PROXY_ALLOWED_HOSTS,
        'tip' => 'Only whitelisted geospatial service hosts are permitted'
    ]);
    exit;
}

// Check for blocked internal paths
if (is_path_blocked($path, $BLOCKED_PATHS)) {
    http_response_code(403);
    echo json_encode([
        'error' => 'Path not allowed',
        'message' => "Access to internal paths is restricted",
        'blocked_patterns' => $BLOCKED_PATHS
    ]);
    exit;
}

// Make the proxy request
$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => $raw_url,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_MAXREDIRS => 3,
    CURLOPT_TIMEOUT => 10,
    CURLOPT_CONNECTTIMEOUT => 5,
    CURLOPT_SSL_VERIFYPEER => false,
    CURLOPT_USERAGENT => 'GeoPortal-Proxy/2.4.1'
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    http_response_code(502);
    echo json_encode([
        'error' => 'Proxy request failed',
        'message' => $error,
        'target_url' => $raw_url
    ]);
    exit;
}

// Return the proxied content
header('X-Proxy-Status: success');
header('X-Original-URL: ' . $raw_url);
header('X-Validated-Host: ' . $hostname);

// Try to detect content type
if (strpos($response, '<?xml') === 0 || strpos($response, '<') === 0) {
    header('Content-Type: text/xml');
} elseif (json_decode($response) !== null) {
    header('Content-Type: application/json');
} else {
    header('Content-Type: text/plain');
}

echo $response;
