<?php
/**
 * Authentication utilities for Axis admin interface.
 * Uses HTTP Basic Authentication for admin access.
 */

define('AXIS_ADMIN_USER', 'admin');
define('AXIS_ADMIN_PASS', 'axis');
define('AXIS_ADMIN_REALM', 'Axis Admin');

function requireAdminAuth() {
    if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW'])) {
        sendAuthChallenge();
        exit;
    }
    
    if ($_SERVER['PHP_AUTH_USER'] !== AXIS_ADMIN_USER || 
        $_SERVER['PHP_AUTH_PW'] !== AXIS_ADMIN_PASS) {
        sendAuthChallenge();
        exit;
    }
    
    return true;
}

function sendAuthChallenge() {
    header('WWW-Authenticate: Basic realm="' . AXIS_ADMIN_REALM . '"');
    header('HTTP/1.0 401 Unauthorized');
    echo '<!DOCTYPE html><html><head><title>401 Unauthorized</title></head>';
    echo '<body><h1>401 Unauthorized</h1>';
    echo '<p>This page requires administrator privileges.</p></body></html>';
}

function isAdminAuthenticated() {
    return isset($_SERVER['PHP_AUTH_USER']) && 
           isset($_SERVER['PHP_AUTH_PW']) &&
           $_SERVER['PHP_AUTH_USER'] === AXIS_ADMIN_USER &&
           $_SERVER['PHP_AUTH_PW'] === AXIS_ADMIN_PASS;
}
