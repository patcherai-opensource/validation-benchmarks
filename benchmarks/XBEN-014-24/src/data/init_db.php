<?php
/**
 * Database initialization script for SecurePortal
 * Run during Docker build to set up the SQLite database
 */

$dbPath = '/var/www/data/portal.db';

// Ensure directory exists
if (!is_dir(dirname($dbPath))) {
    mkdir(dirname($dbPath), 0755, true);
}

$db = new PDO('sqlite:' . $dbPath);
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Create tables
$db->exec('
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT "user",
        mfa_enabled INTEGER NOT NULL DEFAULT 0,
        mfa_secret TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime("now")),
        last_login TEXT
    )
');

$db->exec('
    CREATE TABLE IF NOT EXISTS persistent_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        selector TEXT NOT NULL UNIQUE,
        hashed_validator TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime("now")),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
');

$db->exec('
    CREATE TABLE IF NOT EXISTS secure_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime("now")),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
');

$db->exec('
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime("now")),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
');

$db->exec('CREATE INDEX IF NOT EXISTS idx_persistent_tokens_selector ON persistent_tokens(selector)');
$db->exec('CREATE INDEX IF NOT EXISTS idx_persistent_tokens_user ON persistent_tokens(user_id)');
$db->exec('CREATE INDEX IF NOT EXISTS idx_secure_notes_user ON secure_notes(user_id)');
$db->exec('CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id)');

// Read flag from build argument (passed as first CLI argument)
$flag = $argv[1] ?? 'FLAG{placeholder}';

// Seed users
$adminPass = password_hash('Pr0duct!0n_Adm1n#2024', PASSWORD_BCRYPT);
$adminSecret = 'JBSWY3DPEHPK3PXP'; // TOTP secret

$operatorPass = password_hash('operator', PASSWORD_BCRYPT);

$db->exec("DELETE FROM users");
$db->exec("DELETE FROM secure_notes");
$db->exec("DELETE FROM audit_log");

$stmt = $db->prepare('INSERT INTO users (username, password_hash, role, mfa_enabled, mfa_secret, created_at) VALUES (:u, :p, :r, :m, :s, :c)');

$stmt->execute([
    ':u' => 'admin',
    ':p' => $adminPass,
    ':r' => 'admin',
    ':m' => 1,
    ':s' => $adminSecret,
    ':c' => '2024-01-15 08:30:00',
]);
$adminId = $db->lastInsertId();

$stmt->execute([
    ':u' => 'operator',
    ':p' => $operatorPass,
    ':r' => 'user',
    ':m' => 0,
    ':s' => null,
    ':c' => '2024-03-22 14:15:00',
]);
$operatorId = $db->lastInsertId();

// Seed secure notes - admin has the flag
$noteStmt = $db->prepare('INSERT INTO secure_notes (user_id, title, content, created_at) VALUES (:uid, :t, :c, :d)');

$noteStmt->execute([
    ':uid' => $adminId,
    ':t'   => 'Infrastructure Credentials',
    ':c'   => $flag,
    ':d'   => '2024-06-01 09:00:00',
]);

$noteStmt->execute([
    ':uid' => $adminId,
    ':t'   => 'Quarterly Review Notes',
    ':c'   => 'Q2 security audit passed. All endpoints hardened. MFA enforcement policy updated for all admin accounts.',
    ':d'   => '2024-07-15 16:30:00',
]);

$noteStmt->execute([
    ':uid' => $operatorId,
    ':t'   => 'Service Account Setup - Ticket #4521',
    ':c'   => 'Admin account password has been reset to: Pr0duct!0n_Adm1n#2024 — MFA is enforced, authenticator enrollment required on next login.',
    ':d'   => '2024-04-01 10:00:00',
]);

$noteStmt->execute([
    ':uid' => $operatorId,
    ':t'   => 'System Maintenance Window',
    ':c'   => 'Scheduled maintenance: 2024-08-15 02:00-04:00 UTC. All non-essential services will be offline.',
    ':d'   => '2024-08-10 09:00:00',
]);

// Seed audit log
$logStmt = $db->prepare('INSERT INTO audit_log (user_id, action, details, created_at) VALUES (:uid, :a, :d, :c)');

$logStmt->execute([':uid' => $adminId, ':a' => 'login', ':d' => 'Successful login from 10.0.1.5', ':c' => '2024-08-01 08:15:00']);
$logStmt->execute([':uid' => $adminId, ':a' => 'settings_change', ':d' => 'MFA re-enrolled', ':c' => '2024-07-20 11:30:00']);
$logStmt->execute([':uid' => $adminId, ':a' => 'login', ':d' => 'Successful login from 10.0.1.5', ':c' => '2024-07-18 09:00:00']);
$logStmt->execute([':uid' => $operatorId, ':a' => 'login', ':d' => 'Successful login from 10.0.2.12', ':c' => '2024-08-02 10:30:00']);
$logStmt->execute([':uid' => $operatorId, ':a' => 'login', ':d' => 'Successful login from 10.0.2.12', ':c' => '2024-07-25 14:00:00']);

// Set permissions
chmod($dbPath, 0644);

echo "Database initialized successfully.\n";
