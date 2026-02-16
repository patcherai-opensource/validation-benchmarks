<?php
/**
 * Authentication and session management
 */

session_start();

function auth_check() {
    if (empty($_SESSION['user_id'])) {
        header('Location: /index.php?module=login');
        exit;
    }
}

function auth_check_admin() {
    auth_check();
    if (empty($_SESSION['is_admin'])) {
        http_response_code(403);
        echo '<div class="gp-error">Access denied. Administrator privileges required.</div>';
        exit;
    }
}

function auth_login($username, $password) {
    $db = get_db();
    $stmt = $db->prepare("SELECT rowid, login, pass_crypted, firstname, lastname, admin FROM gp_users WHERE login = ? AND status = 1");
    $stmt->execute([$username]);
    $user = $stmt->fetch();

    if ($user && password_verify($password, $user['pass_crypted'])) {
        $_SESSION['user_id'] = $user['rowid'];
        $_SESSION['user_login'] = $user['login'];
        $_SESSION['user_name'] = $user['firstname'] . ' ' . $user['lastname'];
        $_SESSION['is_admin'] = (int)$user['admin'];

        // Update last login
        $stmt = $db->prepare("UPDATE gp_users SET datelastlogin = NOW() WHERE rowid = ?");
        $stmt->execute([$user['rowid']]);

        return true;
    }
    return false;
}

function auth_logout() {
    session_destroy();
    header('Location: /index.php?module=login');
    exit;
}

function get_current_user_info() {
    return array(
        'id' => $_SESSION['user_id'] ?? 0,
        'login' => $_SESSION['user_login'] ?? '',
        'name' => $_SESSION['user_name'] ?? '',
        'admin' => $_SESSION['is_admin'] ?? 0,
    );
}
