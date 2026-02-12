<?php
session_start();

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

$auth = new AuthManager();
$page = isset($_GET['page']) ? $_GET['page'] : 'home';

// Handle logout
if ($page === 'logout') {
    $auth->logout();
    header('Location: /');
    exit;
}

// Handle remember-me cookie authentication
if (!isset($_SESSION['user_id']) && isset($_COOKIE['REMEMBERME'])) {
    $auth->authenticateFromRememberMe($_COOKIE['REMEMBERME']);
}

// Handle login POST
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $page === 'login') {
    $username = isset($_POST['username']) ? $_POST['username'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    $remember = isset($_POST['remember_me']) ? true : false;

    $result = $auth->login($username, $password, $remember);

    if ($result === 'require_2fa') {
        header('Location: /?page=2fa');
        exit;
    } elseif ($result === 'success') {
        header('Location: /?page=dashboard');
        exit;
    } else {
        $login_error = 'Invalid username or password.';
    }
}

// Handle 2FA verification POST
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $page === '2fa') {
    $code = isset($_POST['code']) ? $_POST['code'] : '';
    if ($auth->verify2FA($code)) {
        header('Location: /?page=dashboard');
        exit;
    } else {
        $twofa_error = 'Invalid verification code. Please try again.';
    }
}

// Determine what to render
$is_authenticated = $auth->isFullyAuthenticated();
$needs_2fa = isset($_SESSION['2fa_pending']) && $_SESSION['2fa_pending'] === true;

include __DIR__ . '/templates/header.php';

if ($page === 'dashboard' && $is_authenticated) {
    include __DIR__ . '/templates/dashboard.php';
} elseif ($page === 'settings' && $is_authenticated) {
    include __DIR__ . '/templates/settings.php';
} elseif ($page === '2fa' && $needs_2fa) {
    include __DIR__ . '/templates/2fa.php';
} elseif ($page === 'login' || (!$is_authenticated && $page !== '2fa')) {
    include __DIR__ . '/templates/login.php';
} else {
    include __DIR__ . '/templates/home.php';
}

include __DIR__ . '/templates/footer.php';
?>

