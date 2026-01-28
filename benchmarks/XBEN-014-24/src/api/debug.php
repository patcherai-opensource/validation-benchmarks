<?php
/**
 * TaskFlow Portal - Debug Endpoint
 * NOTE: This endpoint should be disabled in production
 */
header('Content-Type: application/json');

// Check if debug mode is enabled (simulating misconfiguration)
$debug_mode = true;

if (!$debug_mode) {
    http_response_code(403);
    echo json_encode(['error' => 'Debug mode disabled']);
    exit;
}

// Leak session token info (simulating debug output - this is a security misconfiguration)
$session_info = [
    'debug' => true,
    'warning' => 'Debug endpoint exposed - disable in production',
    'persistent_tokens' => [
        [
            'series' => 'a1b2c3d4e5f6',
            'user_identifier' => 'guest',
            'token_value' => '7f8e9d0c1b2a3456',
            'status' => 'active'
        ],
        [
            'series' => 'f6e5d4c3b2a1',
            'user_identifier' => 'demo_user', 
            'token_value' => '1234567890abcdef',
            'status' => 'active'
        ]
    ],
    'cookie_format' => 'base64(user_identifier:series:token_value)',
    'note' => 'Token validation only checks series and token_value match'
];

echo json_encode($session_info, JSON_PRETTY_PRINT);
