-- Create MySQL user and grant privileges
CREATE USER 'web_db_user'@'localhost' IDENTIFIED BY 'P@ssw0rd123!';
GRANT ALL PRIVILEGES ON aimeos_media.* TO 'web_db_user'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS aimeos_media;

USE aimeos_media;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS media_items (
    media_id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    mimetype VARCHAR(50),
    domain VARCHAR(50),
    uploaded_by INT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    sku VARCHAR(50),
    description TEXT,
    price DECIMAL(10,2)
);

-- Admin user for media management
INSERT INTO users (username, password, email, role) VALUES ('mediaadmin', 'Aimeos2024!secure', 'admin@aimeos-demo.local', 'admin');

-- Sample products
INSERT INTO products (name, sku, description, price) VALUES 
('Premium Widget', 'PRD-001', 'High quality widget for enterprise use', 99.99),
('Basic Gadget', 'PRD-002', 'Entry level gadget for consumers', 29.99),
('Pro Tool Set', 'PRD-003', 'Professional grade tool set', 199.99);
