<?php
/**
 * User profile controller
 */

require_once __DIR__ . '/../lib/middleware.php';

$auth = initializeAuth();
requireFullAuth($auth);

$db = getDatabaseConnection();
$userId = $_SESSION['user_id'];

$stmt = $db->prepare('SELECT username, role, created_at, last_login, mfa_enabled FROM users WHERE id = :id');
$stmt->execute([':id' => $userId]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

require __DIR__ . '/../views/profile.php';
