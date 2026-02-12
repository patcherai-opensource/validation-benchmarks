<?php
/**
 * Authentication and authorization utilities for XWiki Platform.
 */

function get_current_user_info() {
    if (!isset($_SESSION)) {
        session_start();
    }
    if (isset($_SESSION['xwiki_user'])) {
        return $_SESSION['xwiki_user'];
    }
    return null;
}

function require_login() {
    $user = get_current_user_info();
    if (!$user) {
        header('Location: /bin/login');
        exit();
    }
    return $user;
}

function has_right($user, $right) {
    if (!$user || !isset($user['XWU_RIGHTS'])) {
        return false;
    }
    $rights = explode(',', $user['XWU_RIGHTS']);
    return in_array(strtoupper($right), array_map('trim', $rights));
}

function require_right($user, $right) {
    if (!has_right($user, $right)) {
        http_response_code(403);
        echo '<!DOCTYPE html><html><head><title>Access Denied</title><link rel="stylesheet" href="/assets/style.css"></head><body>';
        echo '<div id="xwikimaincontainer"><div class="main-content">';
        echo '<h1>Access Denied</h1>';
        echo '<p>You do not have the <strong>' . htmlspecialchars($right) . '</strong> right required to access this resource.</p>';
        echo '<p>Please contact your wiki administrator to request additional permissions.</p>';
        echo '<p><a href="/">Return to home</a></p>';
        echo '</div></div></body></html>';
        exit();
    }
}
