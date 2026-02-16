<?php
/**
 * Sign-in controller
 * Handles first-factor authentication (username + password)
 */

require_once __DIR__ . '/../lib/middleware.php';

$auth = initializeAuth();
attemptPersistentLogin($auth);

if ($auth->isFullyAuthenticated()) {
    header('Location: /dashboard');
    exit;
}

$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';
    $staySignedIn = isset($_POST['stay_signed_in']);

    if (empty($username) || empty($password)) {
        $error = 'Please enter both username and password.';
    } else {
        $user = $auth->validateCredentials($username, $password);

        if ($user) {
            $auth->startSession($user);

            // Issue persistent auth token if "stay signed in" was checked.
            // The token is generated and cookie is set immediately after
            // password authentication succeeds.
            if ($staySignedIn) {
                $tokenValue = $auth->generatePersistentToken($user['id'], $user['username']);
                $auth->setPersistentCookie($tokenValue);
            }

            // Update last login
            $db = getDatabaseConnection();
            $stmt = $db->prepare('UPDATE users SET last_login = datetime("now") WHERE id = :id');
            $stmt->execute([':id' => $user['id']]);

            if ($auth->isPendingMfa()) {
                header('Location: /auth/verify');
                exit;
            }

            header('Location: /dashboard');
            exit;
        } else {
            // Check if user exists for appropriate error
            $db = getDatabaseConnection();
            $stmt = $db->prepare('SELECT id FROM users WHERE username = :u');
            $stmt->execute([':u' => $username]);
            if ($stmt->fetch()) {
                $error = 'Incorrect password for this account.';
            } else {
                $error = 'Account not found. Please check your username.';
            }
        }
    }
}

require __DIR__ . '/../views/signin.php';
