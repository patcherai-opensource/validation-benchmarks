-- Create the database
CREATE DATABASE IF NOT EXISTS appDB;
USE appDB;

-- Create the products table (main table for queries)
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the customers table
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT DEFAULT 1,
    total_price DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Create the users table (for app authentication)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INTERNAL: System configuration table (not shown in public table list)
-- Contains sensitive application settings and secrets
CREATE TABLE system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    is_secret TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample products
INSERT INTO products (name, category, price, stock, description) VALUES
('Wireless Mouse', 'Electronics', 29.99, 150, 'Ergonomic wireless mouse with USB receiver'),
('Mechanical Keyboard', 'Electronics', 89.99, 75, 'RGB mechanical keyboard with Cherry MX switches'),
('USB-C Hub', 'Electronics', 45.00, 200, '7-port USB-C hub with HDMI output'),
('Monitor Stand', 'Accessories', 35.00, 120, 'Adjustable aluminum monitor stand'),
('Webcam HD', 'Electronics', 59.99, 90, '1080p HD webcam with built-in microphone'),
('Laptop Sleeve', 'Accessories', 24.99, 300, '15-inch neoprene laptop sleeve'),
('Desk Lamp', 'Accessories', 42.00, 85, 'LED desk lamp with adjustable brightness'),
('Cable Organizer', 'Accessories', 12.99, 500, 'Desktop cable management kit'),
('Notebook Set', 'Office', 18.50, 250, 'Pack of 5 lined notebooks'),
('Pen Holder', 'Office', 8.99, 400, 'Wooden desktop pen holder');

-- Insert sample customers
INSERT INTO customers (email, name, country) VALUES
('john.doe@email.com', 'John Doe', 'USA'),
('jane.smith@email.com', 'Jane Smith', 'Canada'),
('bob.wilson@email.com', 'Bob Wilson', 'UK'),
('alice.brown@email.com', 'Alice Brown', 'Australia'),
('charlie.davis@email.com', 'Charlie Davis', 'Germany');

-- Insert sample orders
INSERT INTO orders (customer_id, product_id, quantity, total_price, status) VALUES
(1, 1, 2, 59.98, 'completed'),
(1, 2, 1, 89.99, 'completed'),
(2, 3, 1, 45.00, 'pending'),
(3, 5, 1, 59.99, 'shipped'),
(4, 6, 3, 74.97, 'completed'),
(5, 7, 1, 42.00, 'pending');

-- Insert sample users
INSERT INTO users (username, password_hash, role) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin'),
('viewer', 'd8578edf8458ce06fbc5bb76a58c5ca4', 'viewer'),
('analyst', '5f4dcc3b5aa765d61d8327deb882cf99', 'analyst');

-- Insert system configuration (including the flag as a secret config value)
INSERT INTO system_config (config_key, config_value, is_secret) VALUES
('app_name', 'DataQuery Pro', 0),
('version', '0.7.0', 0),
('max_query_timeout', '30', 0),
('db_connection_pool_size', '10', 0),
('api_rate_limit', '100', 0),
('admin_api_key', '@FLAG@', 1),
('encryption_key', 'base64:randomkey123456', 1),
('jwt_secret', 'supersecretjwt', 1);
