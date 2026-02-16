<?php
/**
 * Authentication utilities
 * Handles member authentication, login recording, and token management
 */

/**
 * Record a login attempt for auditing purposes
 */
function recordLoginAttempt($db, $email, $memberId, $status) {
    $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    $stmt = $db->prepare("INSERT INTO LoginAttempt (Email, MemberID, Status, IP) VALUES (:email, :mid, :status, :ip)");
    $stmt->execute([
        ':email' => $email,
        ':mid' => $memberId,
        ':status' => $status,
        ':ip' => $ip
    ]);
}

/**
 * Register a failed login and increment failure counter
 */
function registerFailedLogin($db, $memberId) {
    $stmt = $db->prepare("UPDATE Member SET FailedLoginCount = FailedLoginCount + 1 WHERE ID = :id");
    $stmt->execute([':id' => $memberId]);

    // Lock account after too many failures
    $stmt = $db->prepare("SELECT FailedLoginCount FROM Member WHERE ID = :id");
    $stmt->execute([':id' => $memberId]);
    $row = $stmt->fetch();

    if ($row && $row['FailedLoginCount'] >= LOCKOUT_THRESHOLD) {
        $lockoutUntil = date('Y-m-d H:i:s', strtotime('+15 minutes'));
        $stmt = $db->prepare("UPDATE Member SET LockedOutUntil = :until WHERE ID = :id");
        $stmt->execute([':until' => $lockoutUntil, ':id' => $memberId]);
    }
}

/**
 * Register a successful login
 */
function registerSuccessfulLogin($db, $memberId) {
    $stmt = $db->prepare("UPDATE Member SET
        FailedLoginCount = 0,
        LockedOutUntil = NULL,
        NumVisit = NumVisit + 1,
        LastVisited = datetime('now')
        WHERE ID = :id");
    $stmt->execute([':id' => $memberId]);
}

/**
 * Generate an autologin token for password reset
 */
function generateAutologinToken() {
    return hash('md5', strval(time()));
}

/**
 * Log password reset event
 * In production this would dispatch an email via configured SMTP transport
 */
function logPasswordResetEvent($email, $token) {
    // Password reset email would be sent here via SMTP
    // The token is stored in the Member record's AutoLoginHash field
    error_log("Password reset requested for: " . $email);
}
