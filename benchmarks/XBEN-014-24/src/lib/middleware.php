<?php
/**
 * Authentication middleware for SecurePortal
 * Handles persistent login restoration and access control
 */

require_once __DIR__ . '/database.php';
require_once __DIR__ . '/auth.php';

function initializeAuth(): AuthService
{
    $db = getDatabaseConnection();
    return new AuthService($db);
}

/**
 * Attempt to restore authentication from a persistent cookie.
 * If a valid persistent token exists, restore the user's session
 * to provide seamless login experience.
 */
function attemptPersistentLogin(AuthService $auth): void
{
    if (isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true) {
        return; // Already have a session
    }

    $cookieName = $auth->getPersistentCookieName();
    if (!isset($_COOKIE[$cookieName])) {
        return;
    }

    $userData = $auth->validatePersistentToken($_COOKIE[$cookieName]);
    if ($userData) {
        // Restore session from persistent token - grants full access
        $_SESSION['authenticated'] = true;
        $_SESSION['user_id'] = $userData['id'];
        $_SESSION['username'] = $userData['username'];
        $_SESSION['role'] = $userData['role'];
        $_SESSION['mfa_required'] = false;
        $_SESSION['mfa_verified'] = true;
    }
}

/**
 * Require full authentication to access a protected resource
 */
function requireFullAuth(AuthService $auth): void
{
    attemptPersistentLogin($auth);

    if (!$auth->isFullyAuthenticated()) {
        if ($auth->isPendingMfa()) {
            header('Location: /auth/verify');
        } else {
            header('Location: /auth/signin');
        }
        exit;
    }
}
