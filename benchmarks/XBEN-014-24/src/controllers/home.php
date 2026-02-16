<?php
/**
 * Home page controller
 */

require_once __DIR__ . '/../lib/middleware.php';

$auth = initializeAuth();
attemptPersistentLogin($auth);

if ($auth->isFullyAuthenticated()) {
    header('Location: /dashboard');
    exit;
}

require __DIR__ . '/../views/home.php';
