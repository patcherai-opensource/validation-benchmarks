<?php
/**
 * Database helper functions
 * SQLite-based storage for users, pages, and configurations
 */

require_once __DIR__ . '/config.php';

function getDB() {
    static $db = null;
    if ($db === null) {
        $db = new SQLite3(DB_PATH);
        $db->busyTimeout(5000);
        $db->exec('PRAGMA journal_mode = WAL');
    }
    return $db;
}

function findUserByApiToken($token) {
    $db = getDB();
    $stmt = $db->prepare('SELECT * FROM users WHERE apiToken = :token AND status = 1');
    $stmt->bindValue(':token', $token, SQLITE3_TEXT);
    $result = $stmt->execute();
    $user = $result->fetchArray(SQLITE3_ASSOC);
    return $user ?: null;
}

function getPageByPath($path) {
    $db = getDB();
    $stmt = $db->prepare('SELECT p.*, u.username as creator_name FROM pages p LEFT JOIN users u ON p.creator = u.id WHERE p.path = :path AND p.status = 1');
    $stmt->bindValue(':path', $path, SQLITE3_TEXT);
    $result = $stmt->execute();
    $page = $result->fetchArray(SQLITE3_ASSOC);
    return $page ?: null;
}

function getChildPages($parentPath) {
    $db = getDB();
    if ($parentPath === '/') {
        $pattern = '/%';
    } else {
        $pattern = $parentPath . '/%';
    }
    $stmt = $db->prepare('SELECT path, title, updatedAt FROM pages WHERE path LIKE :pattern AND path NOT LIKE :deeper AND status = 1 ORDER BY path');
    $stmt->bindValue(':pattern', $pattern, SQLITE3_TEXT);
    $deeper = ($parentPath === '/') ? '/%/%' : $parentPath . '/%/%';
    $stmt->bindValue(':deeper', $deeper, SQLITE3_TEXT);
    $result = $stmt->execute();
    $pages = array();
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $pages[] = $row;
    }
    return $pages;
}

function getRecentPages($limit = 10) {
    $db = getDB();
    $stmt = $db->prepare('SELECT path, title, updatedAt FROM pages WHERE status = 1 ORDER BY updatedAt DESC LIMIT :limit');
    $stmt->bindValue(':limit', $limit, SQLITE3_INTEGER);
    $result = $stmt->execute();
    $pages = array();
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $pages[] = $row;
    }
    return $pages;
}

function searchPages($query) {
    $db = getDB();
    $stmt = $db->prepare('SELECT path, title, body, updatedAt FROM pages WHERE (title LIKE :q OR body LIKE :q2) AND status = 1 ORDER BY updatedAt DESC LIMIT 20');
    $searchTerm = '%' . $query . '%';
    $stmt->bindValue(':q', $searchTerm, SQLITE3_TEXT);
    $stmt->bindValue(':q2', $searchTerm, SQLITE3_TEXT);
    $result = $stmt->execute();
    $pages = array();
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $pages[] = $row;
    }
    return $pages;
}

function getUserById($id) {
    $db = getDB();
    $stmt = $db->prepare('SELECT id, username, name, email, admin, createdAt FROM users WHERE id = :id');
    $stmt->bindValue(':id', $id, SQLITE3_INTEGER);
    $result = $stmt->execute();
    $user = $result->fetchArray(SQLITE3_ASSOC);
    return $user ?: null;
}
