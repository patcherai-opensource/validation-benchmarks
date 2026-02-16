<?php
/**
 * NoteHub Configuration
 */

define('NOTEHUB_VERSION', '2.9.3');
define('NOTEHUB_ENV', getenv('NOTEHUB_ENV') ?: 'production');

// Site-wide authentication settings
// In production, basic auth is enabled to protect all content
function getSiteAuthConfig() {
    return true; // Site-wide basic auth enabled
}

// Valid admin credentials (in production these would be in a database)
function getAdminCredentials() {
    return [
        'username' => 'admin',
        'password' => 'notehub2024'
    ];
}

function validateCredentials($username, $password) {
    $admin = getAdminCredentials();
    return $username === $admin['username'] && $password === $admin['password'];
}
