<?php
/**
 * Sign-out controller
 */

require_once __DIR__ . '/../lib/middleware.php';

$auth = initializeAuth();
$auth->clearPersistentCookie();
$auth->destroySession();

header('Location: /auth/signin');
exit;
