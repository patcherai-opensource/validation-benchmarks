<?php
/**
 * Middleware: Access Token Parser
 *
 * Parses access_token from request query or body parameters.
 * Used for API authentication - allows programmatic access to GROWI resources.
 *
 * If a valid token is found, sets the authenticated user context.
 * If no token is provided or token is invalid, passes through to next middleware.
 */

require_once __DIR__ . '/database.php';

function accessTokenParser() {
    $accessToken = isset($_GET['access_token']) ? $_GET['access_token'] : 
                   (isset($_POST['access_token']) ? $_POST['access_token'] : null);

    if ($accessToken === null || !is_string($accessToken)) {
        return;
    }

    // Look up user by API token
    $user = findUserByApiToken($accessToken);

    if ($user === null) {
        // Token not found - continue without setting user
        return;
    }

    // Set authenticated user in global scope
    $GLOBALS['authenticated_user'] = array(
        'id' => $user['id'],
        'username' => $user['username'],
        'name' => $user['name'],
        'email' => $user['email'],
        'admin' => (bool)$user['admin']
    );
}
