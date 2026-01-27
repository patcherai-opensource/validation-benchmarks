<?php
header('Content-Type: application/json');

echo json_encode([
    'service' => 'BuildFlow CI',
    'version' => '2.3.1',
    'status' => 'operational',
    'endpoints' => [
        '/' => 'Dashboard (authentication required)',
        '/oauth/login' => 'Initiate OAuth SSO login',
        '/oauth/callback' => 'OAuth callback endpoint (requires state parameter)',
        '/api/status' => 'Service status (this endpoint)'
    ],
    'authentication' => [
        'method' => 'OAuth 2.0 with CSRF state token',
        'state_token_format' => 'hex string (16 characters)'
    ]
]);
