<?php
$db = new PDO('sqlite:/var/db/pim.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$db->exec("CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'ROLE_USER',
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)");

$db->exec("CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    parent_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
)");

$db->exec("CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL UNIQUE,
    family TEXT,
    label TEXT,
    description TEXT,
    category_id INTEGER,
    enabled INTEGER DEFAULT 1,
    image_path TEXT,
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

$db->exec("CREATE TABLE IF NOT EXISTS product_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    mime_type TEXT,
    file_size INTEGER,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
)");

// Seed default data if tables are empty
$count = $db->query('SELECT COUNT(*) FROM users')->fetchColumn();
if ($count == 0) {
    $db->exec("INSERT INTO users (username, password_hash, role, first_name, last_name, email) VALUES
        ('admin', '" . password_hash('admin', PASSWORD_DEFAULT) . "', 'ROLE_ADMIN', 'System', 'Administrator', 'admin@pim.local'),
        ('julia', '" . password_hash('julia', PASSWORD_DEFAULT) . "', 'ROLE_CATALOG_MANAGER', 'Julia', 'Stark', 'julia@pim.local'),
        ('mary', '" . password_hash('mary', PASSWORD_DEFAULT) . "', 'ROLE_USER', 'Mary', 'Smith', 'mary@pim.local')
    ");

    $db->exec("INSERT INTO categories (code, label) VALUES
        ('master', 'Master Catalog'),
        ('clothing', 'Clothing'),
        ('electronics', 'Electronics'),
        ('accessories', 'Accessories'),
        ('home_decor', 'Home & Decor')
    ");

    $db->exec("INSERT INTO attribute_groups (code, label, sort_order) VALUES
        ('general', 'General', 1),
        ('marketing', 'Marketing', 2),
        ('technical', 'Technical', 3),
        ('media', 'Media', 4),
        ('erp', 'ERP', 5)
    ");

    $db->exec("INSERT INTO products (identifier, family, label, description, category_id, enabled) VALUES
        ('SKU-001', 'clothing', 'Cotton T-Shirt', 'Premium cotton t-shirt, available in multiple colors', 2, 1),
        ('SKU-002', 'clothing', 'Denim Jacket', 'Classic denim jacket with button closure', 2, 1),
        ('SKU-003', 'electronics', 'Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 3, 1),
        ('SKU-004', 'electronics', 'USB-C Hub', 'Multi-port USB-C hub with HDMI output', 3, 1),
        ('SKU-005', 'accessories', 'Leather Belt', 'Genuine leather belt with brushed metal buckle', 4, 1),
        ('SKU-006', 'home_decor', 'Ceramic Vase', 'Handcrafted ceramic vase, modern design', 5, 1),
        ('SKU-007', 'clothing', 'Wool Sweater', 'Merino wool sweater, crew neck', 2, 0),
        ('SKU-008', 'electronics', 'Bluetooth Speaker', 'Portable waterproof bluetooth speaker', 3, 1)
    ");
}

return $db;
