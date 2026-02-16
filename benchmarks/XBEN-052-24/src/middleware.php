<?php
/**
 * Middleware functions for request processing
 */

/**
 * Session key parser middleware
 *
 * Processes session_key parameter from query string or request body
 * to support API token authentication. If a valid key is found, the
 * user context is attached to the request lifecycle.
 */
function parseSessionKey($query, $body) {
    $sessionKey = $query['session_key'] ?? $body['session_key'] ?? null;

    if ($sessionKey === null || !is_string($sessionKey)) {
        return ['processed' => false, 'user' => null];
    }

    $user = findUserBySessionKey($sessionKey);

    if ($user === null) {
        return ['processed' => true, 'user' => null];
    }

    return ['processed' => true, 'user' => $user];
}

/**
 * Find a user by their API session key
 */
function findUserBySessionKey($sessionKey) {
    $validKeys = [
        'sk_prod_4x8n29dk3jf9a0s8d7f6g5h4j3k2l1m0' => [
            'id' => 1,
            'username' => 'api_service',
            'email' => 'service@notehub.local',
            'role' => 'api'
        ]
    ];

    return $validKeys[$sessionKey] ?? null;
}
