<?php
/**
 * Middleware: Basic Authentication
 *
 * Enforces site-wide HTTP Basic Authentication when enabled.
 * This middleware runs after accessTokenParser in the middleware chain.
 *
 * When an access_token parameter is present in the request, the basic auth
 * check is skipped to allow API token-based access to resources.
 */

require_once __DIR__ . '/config.php';

function enforceBasicAuth() {
    if (!BASIC_AUTH_ENABLED) {
        return true;
    }

    // If access_token was provided (via query or body), skip basic auth
    // to allow API-based access
    $hasAccessToken = isset($_GET['access_token']) || isset($_POST['access_token']);
    if ($hasAccessToken) {
        return true;
    }

    // Check for Basic Auth credentials
    if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW'])) {
        sendAuthChallenge();
        return false;
    }

    if ($_SERVER['PHP_AUTH_USER'] !== BASIC_AUTH_USERNAME ||
        $_SERVER['PHP_AUTH_PW'] !== BASIC_AUTH_PASSWORD) {
        sendAuthChallenge();
        return false;
    }

    return true;
}

function sendAuthChallenge() {
    header('WWW-Authenticate: Basic realm="GROWI Wiki"');
    header('HTTP/1.0 401 Unauthorized');
    echo '<!DOCTYPE html><html><head><title>401 - Unauthorized</title></head>';
    echo '<body><h1>Unauthorized</h1><p>Valid credentials are required to access this resource.</p></body></html>';
    exit;
}
