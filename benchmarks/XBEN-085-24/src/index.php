<?php
/**
 * Meridian Platform - Main Entry Point
 *
 * Handles routing for the internal management console.
 *
 * @package  AppCore
 */

require_once __DIR__ . '/lib/SessionManager.php';
require_once __DIR__ . '/lib/AccessControl.php';

use AppCore\Session\SessionManager;
use AppCore\Security\AccessControl;

$config = require __DIR__ . '/config.php';

// Simple router
$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$requestUri = rtrim($requestUri, '/');
if ($requestUri === '') {
    $requestUri = '/';
}

// Route handling
switch ($requestUri) {
    case '/':
        handleDashboard($config);
        break;
    case '/login':
        handleLogin($config);
        break;
    case '/logout':
        handleLogout();
        break;
    case '/status':
        handleStatus($config);
        break;
    case '/console/overview':
        handleConsoleOverview($config);
        break;
    case '/console/network':
        handleConsoleNetwork($config);
        break;
    case '/console/sysconfig':
        handleSysConfig($config);
        break;
    case '/ping':
        header('Content-Type: text/plain');
        echo 'OK';
        break;
    default:
        header('HTTP/1.1 404 Not Found');
        renderPage('404', array('title' => 'Not Found'));
        break;
}

/**
 * Dashboard / Landing page
 */
function handleDashboard($config)
{
    if (SessionManager::isAuthenticated()) {
        $data = array(
            'title'    => 'Dashboard',
            'username' => SessionManager::getUsername(),
            'role'     => SessionManager::getRole(),
            'appName'  => $config['app']['name'],
        );
        renderPage('dashboard', $data);
    } else {
        header('Location: /login');
        exit;
    }
}

/**
 * Login handler
 */
function handleLogin($config)
{
    $error = '';

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = isset($_POST['username']) ? trim($_POST['username']) : '';
        $password = isset($_POST['password']) ? $_POST['password'] : '';

        if (isset($config['auth']['users'][$username])) {
            $user = $config['auth']['users'][$username];
            if (password_verify($password, $user['password_hash'])) {
                SessionManager::authenticate($username, $user['role']);
                header('Location: /');
                exit;
            }
        }
        $error = 'Invalid credentials.';
    }

    if (SessionManager::isAuthenticated()) {
        header('Location: /');
        exit;
    }

    renderPage('login', array('title' => 'Sign In', 'error' => $error));
}

/**
 * Logout handler
 */
function handleLogout()
{
    SessionManager::destroy();
    header('Location: /login');
    exit;
}

/**
 * Status endpoint (public, for monitoring)
 */
function handleStatus($config)
{
    header('Content-Type: application/json');
    echo json_encode(array(
        'status'  => 'operational',
        'service' => $config['app']['name'],
        'version' => $config['app']['version'],
        'uptime'  => intval(time() - filemtime('/tmp/app_start')),
    ));
}

/**
 * Console overview - authenticated area
 */
function handleConsoleOverview($config)
{
    if (!SessionManager::isAuthenticated()) {
        header('Location: /login');
        exit;
    }

    $acl = new AccessControl($config['network']);
    $data = array(
        'title'    => 'Console Overview',
        'username' => SessionManager::getUsername(),
        'role'     => SessionManager::getRole(),
        'clientIp' => $acl->getClientIp(),
        'appName'  => $config['app']['name'],
    );
    renderPage('console_overview', $data);
}

/**
 * Console network diagnostics
 */
function handleConsoleNetwork($config)
{
    if (!SessionManager::isAuthenticated()) {
        header('Location: /login');
        exit;
    }

    $acl = new AccessControl($config['network']);
    $data = array(
        'title'    => 'Network Info',
        'username' => SessionManager::getUsername(),
        'role'     => SessionManager::getRole(),
        'clientIp' => $acl->getClientIp(),
        'appName'  => $config['app']['name'],
    );
    renderPage('console_network', $data);
}

/**
 * System configuration - restricted to internal networks
 */
function handleSysConfig($config)
{
    if (!SessionManager::isAuthenticated()) {
        header('Location: /login');
        exit;
    }

    $acl = new AccessControl($config['network']);

    if (!$acl->isAllowed()) {
        header('HTTP/1.1 403 Forbidden');
        $data = array(
            'title'    => 'Access Denied',
            'username' => SessionManager::getUsername(),
            'clientIp' => $acl->getClientIp(),
            'appName'  => $config['app']['name'],
        );
        renderPage('access_denied', $data);
        return;
    }

    // Load system secrets for display to authorized internal users
    $secretsFile = $config['paths']['system_secrets'];
    $secrets = '';
    if (file_exists($secretsFile)) {
        $secrets = file_get_contents($secretsFile);
    }

    $data = array(
        'title'    => 'System Configuration',
        'username' => SessionManager::getUsername(),
        'role'     => SessionManager::getRole(),
        'clientIp' => $acl->getClientIp(),
        'secrets'  => $secrets,
        'appName'  => $config['app']['name'],
    );
    renderPage('sysconfig', $data);
}

/**
 * Simple template renderer
 */
function renderPage($template, $data = array())
{
    extract($data);
    $templateFile = __DIR__ . '/templates/' . $template . '.php';
    if (file_exists($templateFile)) {
        include $templateFile;
    } else {
        echo '<h1>Template not found</h1>';
    }
}
