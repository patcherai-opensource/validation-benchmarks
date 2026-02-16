<?php
session_start();

if (!isset($_SESSION['user_id']) || !isset($_SESSION['permission'])) {
    header("Location: ../index.php");
    exit();
}

$current_user_id = $_SESSION['user_id'];
$current_username = $_SESSION['username'];
$current_display_name = $_SESSION['display_name'];
$current_permission = $_SESSION['permission'];

function has_permission($level) {
    $perms = ['viewer' => 0, 'editor' => 1, 'admin' => 2];
    $current = $_SESSION['permission'] ?? 'viewer';
    return ($perms[$current] ?? 0) >= ($perms[$level] ?? 0);
}
?>
