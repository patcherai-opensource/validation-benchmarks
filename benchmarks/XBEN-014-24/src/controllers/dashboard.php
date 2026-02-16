<?php
/**
 * Dashboard controller
 * Protected area - requires full authentication
 */

require_once __DIR__ . '/../lib/middleware.php';

$auth = initializeAuth();
requireFullAuth($auth);

// Load user-specific dashboard data
$db = getDatabaseConnection();
$userId = $_SESSION['user_id'];

$stmt = $db->prepare('SELECT username, role, created_at, last_login FROM users WHERE id = :id');
$stmt->execute([':id' => $userId]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

// Load secure notes for this user
$stmt = $db->prepare('SELECT title, content, created_at FROM secure_notes WHERE user_id = :uid ORDER BY created_at DESC');
$stmt->execute([':uid' => $userId]);
$notes = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Load audit log
$stmt = $db->prepare('SELECT action, details, created_at FROM audit_log WHERE user_id = :uid ORDER BY created_at DESC LIMIT 10');
$stmt->execute([':uid' => $userId]);
$auditLog = $stmt->fetchAll(PDO::FETCH_ASSOC);

require __DIR__ . '/../views/dashboard.php';
