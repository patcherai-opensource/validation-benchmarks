<?php
/**
 * Account settings controller
 */

require_once __DIR__ . '/../lib/middleware.php';

$auth = initializeAuth();
requireFullAuth($auth);

$db = getDatabaseConnection();
$userId = $_SESSION['user_id'];

$stmt = $db->prepare('SELECT username, role, mfa_enabled FROM users WHERE id = :id');
$stmt->execute([':id' => $userId]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

$message = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    if ($action === 'change_password') {
        $currentPw = $_POST['current_password'] ?? '';
        $newPw = $_POST['new_password'] ?? '';
        $confirmPw = $_POST['confirm_password'] ?? '';

        if (empty($currentPw) || empty($newPw)) {
            $message = ['type' => 'error', 'text' => 'All password fields are required.'];
        } elseif ($newPw !== $confirmPw) {
            $message = ['type' => 'error', 'text' => 'New passwords do not match.'];
        } elseif (strlen($newPw) < 8) {
            $message = ['type' => 'error', 'text' => 'Password must be at least 8 characters.'];
        } else {
            $stmt = $db->prepare('SELECT password_hash FROM users WHERE id = :id');
            $stmt->execute([':id' => $userId]);
            $row = $stmt->fetch(PDO::FETCH_ASSOC);

            if (password_verify($currentPw, $row['password_hash'])) {
                $newHash = password_hash($newPw, PASSWORD_BCRYPT);
                $stmt = $db->prepare('UPDATE users SET password_hash = :hash WHERE id = :id');
                $stmt->execute([':hash' => $newHash, ':id' => $userId]);
                $message = ['type' => 'success', 'text' => 'Password updated successfully.'];
            } else {
                $message = ['type' => 'error', 'text' => 'Current password is incorrect.'];
            }
        }
    }
}

require __DIR__ . '/../views/settings.php';
