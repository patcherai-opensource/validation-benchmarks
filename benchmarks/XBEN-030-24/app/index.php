<?php
/**
 * GestiPro ERP - Main Router
 */

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/core/lib/functions.lib.php';
require_once __DIR__ . '/core/auth.php';
require_once __DIR__ . '/core/template.php';

$module = gp_get_post('module', 'home');

// Handle unauthenticated routes
if ($module === 'login') {
    require __DIR__ . '/public/login.php';
    exit;
}

// Handle health check via ping module
if ($module === 'ping') {
    header('Content-Type: text/plain');
    echo 'OK';
    exit;
}

if ($module === 'logout') {
    auth_logout();
    exit;
}

// Redirect unauthenticated users to login
if (empty($_SESSION['user_id'])) {
    if ($module === 'home') {
        // For root access, show login page directly
        require __DIR__ . '/public/login.php';
        exit;
    }
    header('Location: /index.php?module=login');
    exit;
}

// Verify admin for admin module
if ($module === 'admin' && empty($_SESSION['is_admin'])) {
    http_response_code(403);
    gp_page_header('Access Denied');
    echo '<div class="gp-content"><h2>403 - Access Denied</h2><p>Administrator privileges required.</p></div>';
    gp_page_footer();
    exit;
}

switch ($module) {
    case 'home':
        require __DIR__ . '/pages/home.php';
        break;
    case 'employee':
        require __DIR__ . '/employee/index.php';
        break;
    case 'project':
        require __DIR__ . '/pages/projects.php';
        break;
    case 'admin':
        require __DIR__ . '/admin/index.php';
        break;
    default:
        http_response_code(404);
        gp_page_header('Page Not Found');
        echo '<div class="gp-content"><h2>404 - Page Not Found</h2><p>The requested page does not exist.</p></div>';
        gp_page_footer();
        break;
}
