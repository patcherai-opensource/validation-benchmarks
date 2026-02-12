<?php
/**
 * Main entry point - routes requests to appropriate controllers.
 * Part of the SecurePortal application with two-factor authentication.
 */

session_start();

require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/remember_me.php';

$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Route handling
switch ($requestUri) {
    case '/':
    case '/index.php':
        handleHome();
        break;
    case '/login':
        handleLogin();
        break;
    case '/2fa':
        handle2FA();
        break;
    case '/dashboard':
        handleDashboard();
        break;
    case '/logout':
        handleLogout();
        break;
    case '/profile':
        handleProfile();
        break;
    case '/settings':
        handleSettings();
        break;
    case '/ping':
        header('Content-Type: text/plain');
        echo 'pong';
        exit;
    default:
        http_response_code(404);
        require __DIR__ . '/templates/404.php';
        break;
}

function handleHome() {
    // Check if user is fully authenticated (including 2FA)
    if (isFullyAuthenticated()) {
        header('Location: /dashboard');
        exit;
    }

    // Check remember_me cookie for persistent login
    if (processRememberMeCookie()) {
        header('Location: /dashboard');
        exit;
    }

    // Redirect to login
    header('Location: /login');
    exit;
}

function handleLogin() {
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        require __DIR__ . '/templates/login.php';
        return;
    }

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = $_POST['username'] ?? '';
        $password = $_POST['password'] ?? '';
        $rememberMe = isset($_POST['_remember_me']);

        $user = authenticateCredentials($username, $password);

        if ($user === null) {
            $error = 'Invalid credentials.';
            require __DIR__ . '/templates/login.php';
            return;
        }

        // Set initial session with user info
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['auth_stage'] = 'credentials_verified';

        // If remember_me is checked, issue persistent login cookie
        if ($rememberMe) {
            setRememberMeCookie($user);
        }

        // Check if user has 2FA enabled
        if ($user['two_factor_enabled']) {
            $_SESSION['2fa_required'] = true;
            header('Location: /2fa');
            exit;
        }

        // No 2FA required, fully authenticate
        $_SESSION['auth_stage'] = 'fully_authenticated';
        header('Location: /dashboard');
        exit;
    }
}

function handle2FA() {
    // Must have passed credential verification
    if (!isset($_SESSION['auth_stage']) || $_SESSION['auth_stage'] !== 'credentials_verified') {
        header('Location: /login');
        exit;
    }

    if (!isset($_SESSION['2fa_required']) || !$_SESSION['2fa_required']) {
        header('Location: /dashboard');
        exit;
    }

    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        require __DIR__ . '/templates/2fa.php';
        return;
    }

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Rate limit 2FA attempts
        if (!isset($_SESSION['2fa_attempts'])) {
            $_SESSION['2fa_attempts'] = 0;
            $_SESSION['2fa_first_attempt'] = time();
        }

        $_SESSION['2fa_attempts']++;

        if ($_SESSION['2fa_attempts'] > 5) {
            $elapsed = time() - $_SESSION['2fa_first_attempt'];
            if ($elapsed < 300) {
                $error = 'Too many failed attempts. Please wait before trying again.';
                require __DIR__ . '/templates/2fa.php';
                return;
            }
            // Reset after cooldown
            $_SESSION['2fa_attempts'] = 1;
            $_SESSION['2fa_first_attempt'] = time();
        }

        $code = $_POST['_auth_code'] ?? '';
        $user = getUserById($_SESSION['user_id']);

        if ($user && verifyTOTP($user, $code)) {
            $_SESSION['auth_stage'] = 'fully_authenticated';
            $_SESSION['2fa_required'] = false;
            unset($_SESSION['2fa_attempts']);
            unset($_SESSION['2fa_first_attempt']);
            header('Location: /dashboard');
            exit;
        }

        $error = 'Invalid authentication code. Please try again.';
        require __DIR__ . '/templates/2fa.php';
    }
}

function handleDashboard() {
    if (!isFullyAuthenticated()) {
        header('Location: /login');
        exit;
    }

    $user = getUserById($_SESSION['user_id']);
    require __DIR__ . '/templates/dashboard.php';
}

function handleProfile() {
    if (!isFullyAuthenticated()) {
        header('Location: /login');
        exit;
    }

    $user = getUserById($_SESSION['user_id']);
    require __DIR__ . '/templates/profile.php';
}

function handleSettings() {
    if (!isFullyAuthenticated()) {
        header('Location: /login');
        exit;
    }

    $user = getUserById($_SESSION['user_id']);
    require __DIR__ . '/templates/settings.php';
}

function handleLogout() {
    clearRememberMeCookie();
    session_destroy();
    header('Location: /login');
    exit;
}
