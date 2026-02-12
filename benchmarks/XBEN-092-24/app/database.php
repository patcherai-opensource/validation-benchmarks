<?php

$db = new PDO('sqlite:/var/db/pim.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$db->exec("CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    first_name TEXT,
    last_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)");

$db->exec("CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    parent_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)");

$db->exec("CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL UNIQUE,
    family TEXT,
    category_id INTEGER,
    label TEXT,
    description TEXT,
    enabled INTEGER DEFAULT 1,
    media_file TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)");

$db->exec("CREATE TABLE IF NOT EXISTS attribute_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
)");

$db->exec("CREATE TABLE IF NOT EXISTS media_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    mime_type TEXT,
    size INTEGER,
    uploaded_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
)");

// Seed default data if tables are empty
$userCount = $db->query('SELECT COUNT(*) FROM users')->fetchColumn();
if ($userCount == 0) {
    $stmt = $db->prepare('INSERT INTO users (username, password_hash, email, role, first_name, last_name) VALUES (?, ?, ?, ?, ?, ?)');
    $stmt->execute(['admin', password_hash('admin', PASSWORD_DEFAULT), 'admin@example.com', 'admin', 'Admin', 'PIM']);
    $stmt->execute(['julia', password_hash('julia', PASSWORD_DEFAULT), 'julia@example.com', 'catalog_manager', 'Julia', 'Stark']);
    $stmt->execute(['mary', password_hash('mary2024', PASSWORD_DEFAULT), 'mary@example.com', 'user', 'Mary', 'Smith']);

    $db->exec("INSERT INTO categories (code, label) VALUES ('master', 'Master Catalog')");
    $db->exec("INSERT INTO categories (code, label, parent_id) VALUES ('clothing', 'Clothing', 1)");
    $db->exec("INSERT INTO categories (code, label, parent_id) VALUES ('electronics', 'Electronics', 1)");
    $db->exec("INSERT INTO categories (code, label, parent_id) VALUES ('accessories', 'Accessories', 1)");
    $db->exec("INSERT INTO categories (code, label, parent_id) VALUES ('shoes', 'Shoes', 2)");
    $db->exec("INSERT INTO categories (code, label, parent_id) VALUES ('tshirts', 'T-Shirts', 2)");

    $db->exec("INSERT INTO attribute_groups (code, label, sort_order) VALUES ('general', 'General', 1)");
    $db->exec("INSERT INTO attribute_groups (code, label, sort_order) VALUES ('marketing', 'Marketing', 2)");
    $db->exec("INSERT INTO attribute_groups (code, label, sort_order) VALUES ('technical', 'Technical', 3)");
    $db->exec("INSERT INTO attribute_groups (code, label, sort_order) VALUES ('media', 'Media', 4)");

    $db->exec("INSERT INTO products (identifier, family, category_id, label, description, enabled)
        VALUES ('tshirt-white-s', 'clothing', 6, 'White T-Shirt S', 'Classic white cotton t-shirt, size S', 1)");
    $db->exec("INSERT INTO products (identifier, family, category_id, label, description, enabled)
        VALUES ('tshirt-white-m', 'clothing', 6, 'White T-Shirt M', 'Classic white cotton t-shirt, size M', 1)");
    $db->exec("INSERT INTO products (identifier, family, category_id, label, description, enabled)
        VALUES ('sneakers-black-42', 'footwear', 5, 'Black Sneakers 42', 'Casual black sneakers, size 42', 1)");
    $db->exec("INSERT INTO products (identifier, family, category_id, label, description, enabled)
        VALUES ('laptop-pro-15', 'electronics', 3, 'Laptop Pro 15', '15-inch professional laptop', 1)");
    $db->exec("INSERT INTO products (identifier, family, category_id, label, description, enabled)
        VALUES ('watch-silver', 'accessories', 4, 'Silver Watch', 'Stainless steel analog watch', 1)");
}

return $db;
