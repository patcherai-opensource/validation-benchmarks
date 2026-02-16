#!/usr/bin/env php
<?php
/**
 * CatalogHub PIM - Database initialization
 */

$dbPath = __DIR__ . '/data/cataloghub.db';

if (file_exists($dbPath)) {
    unlink($dbPath);
}

$db = new SQLite3($dbPath);
$db->exec('PRAGMA journal_mode=WAL');

// Users table
$db->exec('
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT "contributor",
        first_name TEXT,
        last_name TEXT,
        created_at TEXT,
        last_login TEXT
    )
');

// Categories table (tree structure like Akeneo)
$db->exec('
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        parent_code TEXT,
        created_at TEXT
    )
');

// Attributes table
$db->exec('
    CREATE TABLE attributes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        label TEXT NOT NULL,
        type TEXT NOT NULL,
        attribute_group TEXT DEFAULT "other",
        is_required INTEGER DEFAULT 0,
        is_unique INTEGER DEFAULT 0,
        is_localizable INTEGER DEFAULT 0
    )
');

// Products table
$db->exec('
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        category_id INTEGER,
        price REAL DEFAULT 0,
        status TEXT DEFAULT "draft",
        completeness INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
');

// Media files table
$db->exec('
    CREATE TABLE media_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_filename TEXT NOT NULL,
        storage_path TEXT NOT NULL,
        mime_type TEXT,
        file_size INTEGER,
        uploaded_by TEXT,
        uploaded_at TEXT
    )
');

// Seed users
$users = [
    ['admin', 'admin', 'admin@cataloghub.local', 'admin', 'System', 'Administrator'],
    ['julia', 'julia', 'julia@cataloghub.local', 'manager', 'Julia', 'Stark'],
    ['peter', 'peter', 'peter@cataloghub.local', 'contributor', 'Peter', 'Morgan'],
];

$now = date('Y-m-d H:i:s');
$stmt = $db->prepare('INSERT INTO users (username, password_hash, email, role, first_name, last_name, created_at) VALUES (:user, :pass, :email, :role, :first, :last, :created)');
foreach ($users as $u) {
    $stmt->bindValue(':user', $u[0], SQLITE3_TEXT);
    $stmt->bindValue(':pass', password_hash($u[1], PASSWORD_DEFAULT), SQLITE3_TEXT);
    $stmt->bindValue(':email', $u[2], SQLITE3_TEXT);
    $stmt->bindValue(':role', $u[3], SQLITE3_TEXT);
    $stmt->bindValue(':first', $u[4], SQLITE3_TEXT);
    $stmt->bindValue(':last', $u[5], SQLITE3_TEXT);
    $stmt->bindValue(':created', $now, SQLITE3_TEXT);
    $stmt->execute();
    $stmt->reset();
}

// Seed categories
$categories = [
    ['master', 'Master Catalog', null],
    ['clothing', 'Clothing', 'master'],
    ['shoes', 'Shoes', 'master'],
    ['accessories', 'Accessories', 'master'],
    ['electronics', 'Electronics', 'master'],
    ['tshirts', 'T-Shirts', 'clothing'],
    ['pants', 'Pants', 'clothing'],
    ['sneakers', 'Sneakers', 'shoes'],
    ['watches', 'Watches', 'accessories'],
];

$stmt = $db->prepare('INSERT INTO categories (code, name, parent_code, created_at) VALUES (:code, :name, :parent, :created)');
foreach ($categories as $c) {
    $stmt->bindValue(':code', $c[0], SQLITE3_TEXT);
    $stmt->bindValue(':name', $c[1], SQLITE3_TEXT);
    $stmt->bindValue(':parent', $c[2], $c[2] ? SQLITE3_TEXT : SQLITE3_NULL);
    $stmt->bindValue(':created', $now, SQLITE3_TEXT);
    $stmt->execute();
    $stmt->reset();
}

// Seed attributes
$attributes = [
    ['sku', 'SKU', 'pim_catalog_identifier', 'product', 1, 1, 0],
    ['name', 'Name', 'pim_catalog_text', 'product', 1, 0, 1],
    ['description', 'Description', 'pim_catalog_textarea', 'product', 0, 0, 1],
    ['price', 'Price', 'pim_catalog_price', 'product', 1, 0, 0],
    ['color', 'Color', 'pim_catalog_simpleselect', 'design', 0, 0, 0],
    ['size', 'Size', 'pim_catalog_simpleselect', 'design', 0, 0, 0],
    ['material', 'Material', 'pim_catalog_text', 'technical', 0, 0, 0],
    ['weight', 'Weight', 'pim_catalog_metric', 'technical', 0, 0, 0],
    ['image', 'Main Image', 'pim_catalog_image', 'media', 0, 0, 0],
    ['brand', 'Brand', 'pim_catalog_text', 'marketing', 0, 0, 0],
];

$stmt = $db->prepare('INSERT INTO attributes (code, label, type, attribute_group, is_required, is_unique, is_localizable) VALUES (:code, :label, :type, :group, :req, :uniq, :loc)');
foreach ($attributes as $a) {
    $stmt->bindValue(':code', $a[0], SQLITE3_TEXT);
    $stmt->bindValue(':label', $a[1], SQLITE3_TEXT);
    $stmt->bindValue(':type', $a[2], SQLITE3_TEXT);
    $stmt->bindValue(':group', $a[3], SQLITE3_TEXT);
    $stmt->bindValue(':req', $a[4], SQLITE3_INTEGER);
    $stmt->bindValue(':uniq', $a[5], SQLITE3_INTEGER);
    $stmt->bindValue(':loc', $a[6], SQLITE3_INTEGER);
    $stmt->execute();
    $stmt->reset();
}

// Seed some products
$products = [
    ['TSHIRT-001', 'Classic Cotton T-Shirt', 'Premium cotton t-shirt with comfortable fit', 6, 29.99, 'enabled', 85],
    ['TSHIRT-002', 'Graphic Print Tee', 'Urban style graphic t-shirt', 6, 34.99, 'enabled', 72],
    ['PANTS-001', 'Slim Fit Jeans', 'Dark wash slim fit denim jeans', 7, 79.99, 'enabled', 90],
    ['SNKR-001', 'Urban Runner', 'Lightweight running sneakers', 8, 119.99, 'enabled', 95],
    ['SNKR-002', 'Classic Canvas', 'Vintage style canvas sneakers', 8, 59.99, 'draft', 45],
    ['WATCH-001', 'Chronograph Sport', 'Stainless steel sport watch', 9, 249.99, 'enabled', 88],
    ['ACC-001', 'Leather Belt', 'Genuine leather belt with brushed buckle', 4, 44.99, 'enabled', 78],
    ['ELEC-001', 'Wireless Earbuds', 'Noise-cancelling wireless earbuds', 5, 149.99, 'draft', 60],
];

$stmt = $db->prepare('INSERT INTO products (sku, name, description, category_id, price, status, completeness, created_at, updated_at) VALUES (:sku, :name, :desc, :cat, :price, :status, :comp, :created, :updated)');
$i = 0;
foreach ($products as $p) {
    $createdAt = date('Y-m-d H:i:s', strtotime("-" . (30 - $i * 3) . " days"));
    $updatedAt = date('Y-m-d H:i:s', strtotime("-" . ($i * 5) . " hours"));
    $stmt->bindValue(':sku', $p[0], SQLITE3_TEXT);
    $stmt->bindValue(':name', $p[1], SQLITE3_TEXT);
    $stmt->bindValue(':desc', $p[2], SQLITE3_TEXT);
    $stmt->bindValue(':cat', $p[3], SQLITE3_INTEGER);
    $stmt->bindValue(':price', $p[4], SQLITE3_FLOAT);
    $stmt->bindValue(':status', $p[5], SQLITE3_TEXT);
    $stmt->bindValue(':comp', $p[6], SQLITE3_INTEGER);
    $stmt->bindValue(':created', $createdAt, SQLITE3_TEXT);
    $stmt->bindValue(':updated', $updatedAt, SQLITE3_TEXT);
    $stmt->execute();
    $stmt->reset();
    $i++;
}

$db->close();

echo "Database initialized successfully.\n";
