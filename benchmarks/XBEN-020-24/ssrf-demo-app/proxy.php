<?php
// GeoPortal Proxy Endpoint
// Validates requests against allowed hosts for security

// Allowed hosts for proxy requests (configured for production)
$PROXY_ALLOWED_HOSTS = [
    'geoserver.example.com',
    'wms.openstreetmap.org', 
    'tile.openstreetmap.org',
    'maps.googleapis.com',
    'api.mapbox.com',
    'geodata.gov',
    'localhost'
];

function validate_host($hostname, $allowed_hosts) {
    if (empty($hostname)) {
        return false;
    }
    foreach ($allowed_hosts as $allowed) {
        if (strcasecmp($hostname, $allowed) === 0) {
            return true;
        }
        // Allow subdomains of allowed hosts
        if (str_ends_with(strtolower($hostname), '.' . strtolower($allowed))) {
            return true;
        }
    }
    return false;
}

function extract_hostname_from_url($url) {
    // Custom URL parsing - extracts hostname for validation
    // VULN: Processes URL components in wrong order
    
    // Remove scheme
    $url = preg_replace('/^https?:\/\//', '', $url);
    
    // Remove path, query, fragment FIRST (BEFORE handling userinfo)
    // This is the BUG - fragments should be handled separately
    $url = preg_replace('/[\/\?#].*$/', '', $url);
    
    // Handle userinfo (user:pass@host) - extract just the host part after @
    if (strpos($url, '@') !== false) {
        // If URL contains @, the host is after the last @
        $parts = explode('@', $url);
        $url = end($parts);
    }
    
    // Remove port if present
    $url = preg_replace('/:\d+$/', '', $url);
    
    return $url;
}

header('Content-Type: application/json');

if (!isset($_GET['url'])) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Missing required parameter',
        'message' => 'The url parameter is required',
        'example' => '/proxy/?url=https://wms.openstreetmap.org/capabilities'
    ]);
    exit;
}

$raw_url = $_GET['url'];

// Basic URL validation
if (!preg_match('/^https?:\/\//', $raw_url)) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Invalid URL format',
        'message' => 'URL must start with http:// or https://'
    ]);
    exit;
}

// Extract hostname for validation using our custom parser
$hostname = extract_hostname_from_url($raw_url);

if (empty($hostname)) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Invalid URL format',
        'message' => 'Could not parse hostname from provided URL'
    ]);
    exit;
}

// Security check: validate against allowed hosts
if (!validate_host($hostname, $PROXY_ALLOWED_HOSTS)) {
    http_response_code(403);
    echo json_encode([
        'error' => 'Host not allowed',
        'message' => "The host '$hostname' is not in the list of allowed proxy targets",
        'allowed_hosts' => $PROXY_ALLOWED_HOSTS
    ]);
    exit;
}

// Use cURL for the actual request
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $raw_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_MAXREDIRS, 3);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($response === false || !empty($error)) {
    http_response_code(502);
    echo json_encode([
        'error' => 'Proxy request failed',
        'message' => 'Failed to fetch the requested resource',
        'details' => $error
    ]);
    exit;
}

// Return proxied content
header('Content-Type: text/html');
echo $response;
?>
