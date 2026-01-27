<?php
/**
 * GeoPortal Proxy Service
 * Proxies requests to external WMS/WFS endpoints
 * Security: Only whitelisted domains are allowed
 */

// Allowed hosts for proxying - security whitelist
$PROXY_ALLOWED_HOSTS = array(
    'openstreetmap.org',
    'geoserver.org', 
    'mapbox.com',
    'arcgisonline.com',
    'tile.openstreetmap.org',
    'localhost',
    '127.0.0.1'
);

/**
 * Extract hostname from URL for validation
 * VULNERABILITY: Uses parse_url which can be bypassed with URL encoding tricks
 */
function extract_hostname($raw_url) {
    $url_parts = parse_url($raw_url);
    return isset($url_parts['host']) ? $url_parts['host'] : null;
}

/**
 * Validate if the hostname is in the whitelist
 */
function validate_host($hostname, $allowed_hosts) {
    if (empty($hostname)) {
        return false;
    }
    
    foreach ($allowed_hosts as $allowed) {
        // Check if hostname matches or is a subdomain of allowed host
        if ($hostname === $allowed || 
            substr($hostname, -strlen('.' . $allowed)) === '.' . $allowed) {
            return true;
        }
    }
    return false;
}

/**
 * Process and proxy the request
 * VULNERABILITY: Validation uses parsed hostname but request uses raw URL
 * allowing bypass via URL userinfo parsing inconsistencies
 */
function proxy_request($raw_url, $allowed_hosts) {
    // Extract hostname for validation
    $hostname = extract_hostname($raw_url);
    
    if ($hostname === null) {
        return array('error' => 'Invalid URL format', 'code' => 400);
    }
    
    // Validate against whitelist using extracted hostname
    if (!validate_host($hostname, $allowed_hosts)) {
        error_log("Proxy request blocked: hostname '$hostname' not in whitelist");
        return array(
            'error' => "Access denied: hostname '$hostname' is not in the allowed hosts list",
            'code' => 403,
            'allowed_hosts' => $allowed_hosts
        );
    }
    
    // VULNERABLE: Hostname validated, but we use the raw_url for the actual request
    // This allows bypass when URL contains userinfo that tricks the validation
    
    // URL decode the raw URL before making request (this is where the bypass happens)
    // The validation saw one hostname, but file_get_contents sees another after decoding
    $request_url = urldecode($raw_url);
    
    $context = stream_context_create(array(
        'http' => array(
            'timeout' => 10,
            'follow_location' => true,
            'max_redirects' => 3,
            'user_agent' => 'GeoPortal-Proxy/3.2.1'
        )
    ));
    
    $content = @file_get_contents($request_url, false, $context);
    
    if ($content === false) {
        $error = error_get_last();
        return array(
            'error' => 'Failed to fetch remote resource: ' . ($error['message'] ?? 'Unknown error'),
            'code' => 502
        );
    }
    
    return array('content' => $content, 'code' => 200);
}

// Main execution
header('Content-Type: application/json');

if (!isset($_GET['url']) || empty($_GET['url'])) {
    http_response_code(400);
    echo json_encode(array(
        'status' => 'error',
        'message' => 'Missing required parameter: url',
        'usage' => '/proxy/?url=<external_url>',
        'allowed_hosts' => $PROXY_ALLOWED_HOSTS
    ), JSON_PRETTY_PRINT);
    exit;
}

$raw_url = $_GET['url'];

// Log the request for debugging
error_log("Proxy request received for URL: $raw_url");

$result = proxy_request($raw_url, $PROXY_ALLOWED_HOSTS);

if (isset($result['error'])) {
    http_response_code($result['code']);
    echo json_encode(array(
        'status' => 'error',
        'message' => $result['error'],
        'allowed_hosts' => $result['allowed_hosts'] ?? $PROXY_ALLOWED_HOSTS
    ), JSON_PRETTY_PRINT);
} else {
    // Success - return the proxied content
    header('Content-Type: text/plain');
    echo $result['content'];
}
?>
