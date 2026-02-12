<?php
// Database initialization script - runs at build time
$dbPath = '/var/www/html/data';
if (!is_dir($dbPath)) {
    mkdir($dbPath, 0755, true);
}

$db = new PDO('sqlite:' . $dbPath . '/aimeos.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Users table - mimics aimeos admin user structure
$db->exec("CREATE TABLE IF NOT EXISTS mshop_customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    siteid TEXT NOT NULL DEFAULT '',
    code TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL DEFAULT '',
    salutation TEXT NOT NULL DEFAULT '',
    company TEXT NOT NULL DEFAULT '',
    firstname TEXT NOT NULL DEFAULT '',
    lastname TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    password TEXT NOT NULL,
    status INTEGER NOT NULL DEFAULT 1,
    vdate TEXT DEFAULT NULL,
    birthday TEXT DEFAULT NULL,
    editor TEXT NOT NULL DEFAULT '',
    mtime TEXT NOT NULL DEFAULT '',
    ctime TEXT NOT NULL DEFAULT '',
    roleid INTEGER NOT NULL DEFAULT 0
)");

// Media table - mimics aimeos media structure
$db->exec("CREATE TABLE IF NOT EXISTS mshop_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    siteid TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL DEFAULT 'default',
    label TEXT NOT NULL DEFAULT '',
    domain TEXT NOT NULL DEFAULT 'product',
    languageid TEXT DEFAULT NULL,
    url TEXT NOT NULL DEFAULT '',
    preview TEXT NOT NULL DEFAULT '',
    mimetype TEXT NOT NULL DEFAULT '',
    status INTEGER NOT NULL DEFAULT 1,
    filesystem TEXT NOT NULL DEFAULT 'fs-media',
    editor TEXT NOT NULL DEFAULT '',
    mtime TEXT NOT NULL DEFAULT '',
    ctime TEXT NOT NULL DEFAULT ''
)");

// Media list table - for relating media to products
$db->exec("CREATE TABLE IF NOT EXISTS mshop_media_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parentid INTEGER NOT NULL,
    siteid TEXT NOT NULL DEFAULT '',
    domain TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL DEFAULT 'default',
    refid TEXT NOT NULL DEFAULT '',
    config TEXT NOT NULL DEFAULT '{}',
    pos INTEGER NOT NULL DEFAULT 0,
    status INTEGER NOT NULL DEFAULT 1,
    mtime TEXT NOT NULL DEFAULT '',
    ctime TEXT NOT NULL DEFAULT '',
    editor TEXT NOT NULL DEFAULT ''
)");

// Product table
$db->exec("CREATE TABLE IF NOT EXISTS mshop_product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    siteid TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL DEFAULT 'default',
    code TEXT NOT NULL DEFAULT '',
    label TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    dataset TEXT NOT NULL DEFAULT '',
    config TEXT NOT NULL DEFAULT '{}',
    status INTEGER NOT NULL DEFAULT 1,
    scale REAL NOT NULL DEFAULT 1,
    start TEXT DEFAULT NULL,
    end TEXT DEFAULT NULL,
    editor TEXT NOT NULL DEFAULT '',
    mtime TEXT NOT NULL DEFAULT '',
    ctime TEXT NOT NULL DEFAULT '',
    target TEXT NOT NULL DEFAULT '',
    boost REAL NOT NULL DEFAULT 1
)");

// Locale/site table
$db->exec("CREATE TABLE IF NOT EXISTS mshop_locale_site (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL DEFAULT '',
    label TEXT NOT NULL DEFAULT '',
    config TEXT NOT NULL DEFAULT '{}',
    status INTEGER NOT NULL DEFAULT 1,
    editor TEXT NOT NULL DEFAULT '',
    mtime TEXT NOT NULL DEFAULT '',
    ctime TEXT NOT NULL DEFAULT '',
    parentid INTEGER DEFAULT NULL,
    level INTEGER NOT NULL DEFAULT 0,
    nleft INTEGER NOT NULL DEFAULT 0,
    nright INTEGER NOT NULL DEFAULT 0
)");

// Insert default site
$db->exec("INSERT INTO mshop_locale_site (code, label, config, status, editor, mtime, ctime, level, nleft, nright)
    VALUES ('default', 'Aimeos', '{\"resource\":{\"fs\":{\"adapter\":\"Standard\",\"basedir\":\"/var/www/html/media\"}}}', 1, 'system', datetime('now'), datetime('now'), 0, 1, 2)");

// Insert default admin user (editor role)
$password = password_hash('editor2024!', PASSWORD_DEFAULT);
$db->exec("INSERT INTO mshop_customer (siteid, code, label, firstname, lastname, email, password, status, editor, mtime, ctime, roleid)
    VALUES ('default', 'editor', 'Content Editor', 'Sarah', 'Mitchell', 'editor@encoder64blog.local', '$password', 1, 'system', datetime('now'), datetime('now'), 2)");

// Insert admin user (admin role - stronger password, not discoverable)
$adminPassword = password_hash(bin2hex(random_bytes(32)), PASSWORD_DEFAULT);
$db->exec("INSERT INTO mshop_customer (siteid, code, label, firstname, lastname, email, password, status, editor, mtime, ctime, roleid)
    VALUES ('default', 'admin', 'Administrator', 'Alex', 'Chen', 'admin@encoder64blog.local', '$adminPassword', 1, 'system', datetime('now'), datetime('now'), 1)");

// Insert some sample products
$products = [
    ['default', 'default', 'BLOG-THEME-01', 'Premium Blog Theme - Minimal', '/products/theme-minimal', '{}', 1],
    ['default', 'default', 'BLOG-THEME-02', 'Premium Blog Theme - Dark Mode', '/products/theme-dark', '{}', 1],
    ['default', 'default', 'BLOG-PLUGIN-01', 'SEO Optimization Plugin', '/products/seo-plugin', '{}', 1],
    ['default', 'default', 'BLOG-PLUGIN-02', 'Social Media Integration', '/products/social-media', '{}', 1],
];

$stmt = $db->prepare("INSERT INTO mshop_product (siteid, type, code, label, url, config, status, editor, mtime, ctime)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'system', datetime('now'), datetime('now'))");

foreach ($products as $p) {
    $stmt->execute($p);
}

// Insert some sample media entries
$media = [
    ['default', 'default', 'product', 'Theme Minimal Preview', 'media/uploads/theme-minimal-preview.jpg', 'image/jpeg', 1],
    ['default', 'default', 'product', 'Theme Dark Preview', 'media/uploads/theme-dark-preview.jpg', 'image/jpeg', 1],
    ['default', 'default', 'product', 'SEO Plugin Banner', 'media/uploads/seo-banner.png', 'image/png', 1],
];

$stmt = $db->prepare("INSERT INTO mshop_media (siteid, type, domain, label, url, mimetype, status, editor, mtime, ctime)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'system', datetime('now'), datetime('now'))");

foreach ($media as $m) {
    $stmt->execute($m);
}

echo "Database initialized successfully.\n";
