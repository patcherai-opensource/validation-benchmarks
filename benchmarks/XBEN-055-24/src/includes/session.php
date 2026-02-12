<?php
/**
 * Session management for SilverStripe Security module
 */

function ss_session_start() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
}

function ss_get_current_member() {
    ss_session_start();
    if (isset($_SESSION['member_id'])) {
        $db = SS_Database::getConn();
        $stmt = $db->prepare("SELECT ID, FirstName, Surname, Email, MemberGroup FROM Member WHERE ID = :id");
        $stmt->bindValue(':id', $_SESSION['member_id'], SQLITE3_INTEGER);
        $result = $stmt->execute();
        return $result->fetchArray(SQLITE3_ASSOC);
    }
    return null;
}

function ss_login_member($memberId) {
    ss_session_start();
    $_SESSION['member_id'] = $memberId;
    $_SESSION['login_time'] = time();
}

function ss_logout_member() {
    ss_session_start();
    session_destroy();
}

function ss_require_login() {
    $member = ss_get_current_member();
    if (!$member) {
        header('Location: /Security/login');
        exit;
    }
    return $member;
}

function ss_require_admin() {
    $member = ss_require_login();
    if ($member['MemberGroup'] !== 'administrators') {
        header('HTTP/1.1 403 Forbidden');
        include __DIR__ . '/../templates/error_403.php';
        exit;
    }
    return $member;
}
?>