<?php
/**
 * Database configuration and initialization
 * Simple SQLite database for user sessions
 */

function getDb() {
    static $db = null;
    if ($db === null) {
        $dbPath = '/tmp/website_builder.db';
        $db = new SQLite3($dbPath);
        
        // Initialize tables
        $db->exec("CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'editor',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");
        
        $db->exec("CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");
        
        // Insert default users if not exist
        $result = $db->querySingle("SELECT COUNT(*) FROM users");
        if ($result == 0) {
            $adminPass = password_hash('admin', PASSWORD_DEFAULT);
            $editorPass = password_hash('editor', PASSWORD_DEFAULT);
            $db->exec("INSERT INTO users (username, password, role) VALUES ('admin', '$adminPass', 'admin')");
            $db->exec("INSERT INTO users (username, password, role) VALUES ('editor', '$editorPass', 'editor')");
        }
    }
    return $db;
}

function authenticate($username, $password) {
    $db = getDb();
    $stmt = $db->prepare("SELECT id, username, password, role FROM users WHERE username = :username");
    $stmt->bindValue(':username', $username, SQLITE3_TEXT);
    $result = $stmt->execute();
    
    if ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        if (password_verify($password, $row['password'])) {
            return array(
                'id' => $row['id'],
                'username' => $row['username'],
                'role' => $row['role']
            );
        }
    }
    return false;
}

function createSession($userId) {
    $db = getDb();
    $token = bin2hex(random_bytes(32));
    $stmt = $db->prepare("INSERT INTO sessions (user_id, session_token) VALUES (:user_id, :token)");
    $stmt->bindValue(':user_id', $userId, SQLITE3_INTEGER);
    $stmt->bindValue(':token', $token, SQLITE3_TEXT);
    $stmt->execute();
    return $token;
}

function validateSession($token) {
    if (empty($token)) return false;
    
    $db = getDb();
    $stmt = $db->prepare("SELECT u.id, u.username, u.role FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.session_token = :token");
    $stmt->bindValue(':token', $token, SQLITE3_TEXT);
    $result = $stmt->execute();
    
    if ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        return $row;
    }
    return false;
}

function destroySession($token) {
    $db = getDb();
    $stmt = $db->prepare("DELETE FROM sessions WHERE session_token = :token");
    $stmt->bindValue(':token', $token, SQLITE3_TEXT);
    $stmt->execute();
}
?>
