<?php
// Initialize SQLite database for wishlist products

$db_path = '/var/www/html/data/wishlist.db';
$db_dir = dirname($db_path);

// Create data directory if it doesn't exist
if (!file_exists($db_dir)) {
    mkdir($db_dir, 0755, true);
}

// Only initialize if database doesn't exist
if (!file_exists($db_path)) {
    $db = new SQLite3($db_path);
    
    // Create products table
    $db->exec('CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT NOT NULL,
        added_date TEXT NOT NULL
    )');
    
    // Create secrets table (contains flag)
    $db->exec('CREATE TABLE IF NOT EXISTS config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT NOT NULL,
        setting_value TEXT NOT NULL
    )');
    
    // Insert sample products
    $products = [
        ['Wireless Headphones', 79.99, 'Electronics', '2024-01-15'],
        ['Running Shoes', 129.99, 'Sports', '2024-01-18'],
        ['Coffee Maker', 49.99, 'Kitchen', '2024-01-20'],
        ['Yoga Mat', 29.99, 'Sports', '2024-01-22'],
        ['Bluetooth Speaker', 59.99, 'Electronics', '2024-02-01'],
        ['Leather Wallet', 45.00, 'Accessories', '2024-02-05'],
        ['Smart Watch', 199.99, 'Electronics', '2024-02-10'],
        ['Camping Tent', 149.99, 'Outdoor', '2024-02-14']
    ];
    
    foreach ($products as $p) {
        $stmt = $db->prepare('INSERT INTO products (name, price, category, added_date) VALUES (?, ?, ?, ?)');
        $stmt->bindValue(1, $p[0], SQLITE3_TEXT);
        $stmt->bindValue(2, $p[1], SQLITE3_FLOAT);
        $stmt->bindValue(3, $p[2], SQLITE3_TEXT);
        $stmt->bindValue(4, $p[3], SQLITE3_TEXT);
        $stmt->execute();
    }
    
    // Insert flag into config table
    $flag = getenv('FLAG') ?: 'FLAG{placeholder}';
    $stmt = $db->prepare('INSERT INTO config (setting_name, setting_value) VALUES (?, ?)');
    $stmt->bindValue(1, 'secret_key', SQLITE3_TEXT);
    $stmt->bindValue(2, $flag, SQLITE3_TEXT);
    $stmt->execute();
    
    $db->close();
}
?>
