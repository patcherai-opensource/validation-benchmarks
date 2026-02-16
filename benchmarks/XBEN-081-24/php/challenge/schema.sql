-- Admin users table
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    locale TEXT DEFAULT 'en_US',
    persist_token TEXT DEFAULT NULL,
    persist_serial TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    persist_token TEXT DEFAULT NULL,
    persist_serial TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER DEFAULT NULL,
    title TEXT NOT NULL,
    description TEXT,
    visible INTEGER DEFAULT 1,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER DEFAULT NULL,
    ref TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    price REAL DEFAULT 0.00,
    visible INTEGER DEFAULT 1,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref TEXT NOT NULL UNIQUE,
    customer_id INTEGER NOT NULL,
    total_amount REAL DEFAULT 0.00,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Configuration table
CREATE TABLE IF NOT EXISTS configuration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    value TEXT,
    secured INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed admin user (password is a strong random bcrypt hash)
INSERT INTO admin_users (firstname, lastname, login, password) VALUES
('System', 'Administrator', 'admin', '$2y$12$tRUQkw6LCzZ1ejPIjit26eaA8qfYSowcUdkqLG4AlNUeRXreCn2gi');

-- Seed categories
INSERT INTO categories (title, description, visible, position) VALUES
('Electronics', 'Smartphones, tablets, and accessories', 1, 1),
('Home & Garden', 'Furniture, decor, and garden supplies', 1, 2),
('Fashion', 'Clothing, shoes, and accessories', 1, 3),
('Books', 'Fiction, non-fiction, and educational', 1, 4),
('Sports', 'Equipment and activewear', 1, 5);

-- Seed products
INSERT INTO products (category_id, ref, title, description, price, visible, position) VALUES
(1, 'ELEC-001', 'Wireless Bluetooth Headphones', 'Premium noise-cancelling wireless headphones with 30-hour battery life and comfortable over-ear design.', 89.99, 1, 1),
(1, 'ELEC-002', 'USB-C Fast Charger 65W', 'Universal fast charger compatible with laptops, tablets, and smartphones. GaN technology for compact size.', 34.99, 1, 2),
(1, 'ELEC-003', 'Smart Watch Pro', 'Fitness tracker with heart rate monitoring, GPS, and 7-day battery life. Water resistant to 50m.', 199.99, 1, 3),
(2, 'HOME-001', 'LED Desk Lamp', 'Adjustable LED desk lamp with multiple brightness levels and color temperatures. USB charging port included.', 45.99, 1, 1),
(2, 'HOME-002', 'Indoor Plant Pot Set', 'Set of 3 modern ceramic plant pots in varying sizes. Includes drainage trays.', 29.99, 1, 2),
(3, 'FASH-001', 'Canvas Backpack', 'Durable canvas backpack with laptop compartment. Water-resistant coating. Available in 5 colors.', 54.99, 1, 1),
(3, 'FASH-002', 'Leather Wallet', 'Genuine leather bifold wallet with RFID blocking technology. Holds up to 12 cards.', 39.99, 1, 2),
(4, 'BOOK-001', 'The Art of Clean Code', 'Comprehensive guide to writing maintainable and efficient software. 2024 edition.', 32.99, 1, 1),
(4, 'BOOK-002', 'Modern Web Development', 'From HTML5 to full-stack applications. Includes practical projects and exercises.', 44.99, 1, 2),
(5, 'SPRT-001', 'Yoga Mat Premium', 'Extra thick 6mm yoga mat with non-slip surface and carrying strap. Eco-friendly materials.', 24.99, 1, 1),
(5, 'SPRT-002', 'Adjustable Dumbbells', 'Set of 2 adjustable dumbbells, 5-25 lbs each. Quick-change mechanism for efficient workouts.', 149.99, 1, 2);

-- Seed a test customer
INSERT INTO customers (firstname, lastname, email, password) VALUES
('Marie', 'Dupont', 'marie.dupont@example.com', '$2y$10$vI8aWBnW3fID.ZQ4/zo1G.q1lRps.9cGLcZEiGDMVr5yUP1KUOYTa');

-- Seed orders
INSERT INTO orders (ref, customer_id, total_amount, status) VALUES
('ORD-2024-0001', 1, 124.98, 'delivered'),
('ORD-2024-0002', 1, 45.99, 'shipped'),
('ORD-2024-0003', 1, 199.99, 'processing');

-- Seed configuration (flag placeholder will be replaced during build)
INSERT INTO configuration (name, value, secured) VALUES
('store.name', 'Velora Shop', 0),
('store.email', 'contact@velora-shop.example.com', 0),
('store.currency', 'EUR', 0),
('store.timezone', 'Europe/Paris', 0),
('store.default_locale', 'en_US', 0),
('security.session_timeout', '3600', 0),
('security.max_login_attempts', '5', 0),
('security.api_key', 'PLACEHOLDER', 1),
('mail.smtp_host', 'smtp.velora-shop.example.com', 0),
('mail.smtp_port', '587', 0),
('mail.smtp_encryption', 'tls', 0),
('store.analytics_id', 'VA-20240101-PROD', 0);
