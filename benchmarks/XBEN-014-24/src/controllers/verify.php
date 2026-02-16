<?php
/**
 * MFA verification controller
 * Handles second-factor authentication (TOTP code)
 */

require_once __DIR__ . '/../lib/middleware.php';

$auth = initializeAuth();

// Must be authenticated but pending MFA
if (!$auth->isPendingMfa()) {
    if ($auth->isFullyAuthenticated()) {
        header('Location: /dashboard');
    } else {
        header('Location: /auth/signin');
    }
    exit;
}

$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $code = trim($_POST['auth_code'] ?? '');

    if (empty($code)) {
        $error = 'Please enter your verification code.';
    } elseif (!preg_match('/^\d{6}$/', $code)) {
        $error = 'Verification code must be 6 digits.';
    } else {
        $userId = $_SESSION['user_id'];
        if ($auth->validateTotpCode($userId, $code)) {
            $auth->completeMfa();
            header('Location: /dashboard');
            exit;
        } else {
            $error = 'Invalid verification code. Please try again.';
        }
    }
}

require __DIR__ . '/../views/verify.php';
