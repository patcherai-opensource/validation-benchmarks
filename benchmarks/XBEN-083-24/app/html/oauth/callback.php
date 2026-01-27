<?php
session_start();

header('Content-Type: application/json');

$FLAG = getenv('FLAG') ?: 'FLAG{placeholder}';

// Get the state parameter from the request
$provided_state = isset($_GET['state']) ? $_GET['state'] : '';

// Check if we have a valid session with a state token
if (!isset($_SESSION['oauth_state'])) {
    http_response_code(400);
    echo json_encode([
        'error' => 'invalid_session',
        'message' => 'No OAuth session found. Please initiate login first at /oauth/login'
    ]);
    exit;
}

$expected_state = $_SESSION['oauth_state'];

// VULNERABLE: Non-constant-time string comparison
// This is the vulnerability from CVE-2023-41936
// The comparison stops at the first mismatched character, 
// causing timing differences that can be exploited
function vulnerable_compare($a, $b) {
    if (strlen($a) !== strlen($b)) {
        return false;
    }
    
    // Character-by-character comparison with intentional timing leak
    // This simulates the behavior of String.equals() in Java
    for ($i = 0; $i < strlen($a); $i++) {
        // Add a small artificial delay for each matching character
        // This makes the timing attack more feasible in a CTF context
        if ($a[$i] === $b[$i]) {
            // Matching character - add small delay
            usleep(5000); // 5ms per matching character
        } else {
            // Mismatch found - return immediately (this is the vulnerability)
            return false;
        }
    }
    return true;
}

// Validate the state token using vulnerable comparison
if (empty($provided_state)) {
    http_response_code(400);
    echo json_encode([
        'error' => 'missing_state',
        'message' => 'State parameter is required'
    ]);
    exit;
}

if (!vulnerable_compare($expected_state, $provided_state)) {
    http_response_code(401);
    echo json_encode([
        'error' => 'invalid_state', 
        'message' => 'State token validation failed'
    ]);
    exit;
}

// State validated successfully - authentication bypass achieved!
$_SESSION['authenticated'] = true;

echo json_encode([
    'success' => true,
    'message' => 'Authentication successful',
    'user' => [
        'id' => 'admin',
        'role' => 'administrator',
        'permissions' => ['read', 'write', 'admin']
    ],
    'admin_secret' => $FLAG
]);
