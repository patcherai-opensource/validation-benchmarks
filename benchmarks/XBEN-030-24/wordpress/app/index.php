<?php
session_start();
require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/functions.php';

// Handle logout
if (isset($_GET['page']) && $_GET['page'] === 'auth' && isset($_GET['logout'])) {
    session_destroy();
    header('Location: /');
    exit;
}

// Handle login POST
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username'], $_POST['password'])) {
    if ($_POST['username'] === RASPI_ADMIN_USER && password_verify($_POST['password'], RASPI_ADMIN_PASS)) {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $_POST['username'];
        $_SESSION['login_time'] = time();
        generateCsrfToken();
        header('Location: /?page=wg_conf');
        exit;
    } else {
        $login_error = 'Invalid credentials';
    }
}

// Show login page if not authenticated
if (!isAuthenticated()) {
    include __DIR__ . '/templates/login.php';
    exit;
}

// Check session timeout
if (isset($_SESSION['login_time']) && (time() - $_SESSION['login_time']) > RASPI_SESSION_TIMEOUT) {
    session_destroy();
    header('Location: /');
    exit;
}

// Route to appropriate page
$page = isset($_GET['page']) ? $_GET['page'] : 'dashboard';
$validPages = array('dashboard', 'wlan0_info', 'dhcpd_conf', 'hostapd_conf', 'wg_conf', 'openvpn_conf', 'system_info', 'about');

if (!in_array($page, $validPages)) {
    $page = 'dashboard';
}

$csrf_token = generateCsrfToken();
$systemInfo = getSystemInfo();

include __DIR__ . '/templates/header.php';
include __DIR__ . '/templates/' . $page . '.php';
include __DIR__ . '/templates/footer.php';
