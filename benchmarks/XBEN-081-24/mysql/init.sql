CREATE DATABASE IF NOT EXISTS app_db;

CREATE USER 'db_username'@'%' IDENTIFIED BY 'pCxvkPyS9JYq27BVdUX4N8';

GRANT ALL PRIVILEGES ON app_db.* TO 'db_username'@'%';

FLUSH PRIVILEGES;

USE app_db;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS admin_notes;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS config;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) DEFAULT '',
    lastname VARCHAR(255) DEFAULT '',
    locale VARCHAR(10) DEFAULT 'en_US',
    algo VARCHAR(128) DEFAULT NULL,
    salt VARCHAR(128) DEFAULT NULL,
    remember_me_token VARCHAR(255) DEFAULT NULL,
    remember_me_serial VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) DEFAULT '',
    lastname VARCHAR(255) DEFAULT '',
    email VARCHAR(255) DEFAULT NULL,
    remember_me_token VARCHAR(255) DEFAULT NULL,
    remember_me_serial VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE admin_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    title VARCHAR(256) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE CASCADE
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    ref VARCHAR(64) NOT NULL,
    status_id INT DEFAULT 1,
    invoice_date DATETIME DEFAULT NULL,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'EUR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
);

CREATE TABLE config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO config (name, value) VALUES
('store.name', 'Demo Store'),
('store.email', 'admin@demo-store.local'),
('store.currency', 'EUR'),
('store.default_locale', 'en_US'),
('session.timeout', '3600');

INSERT INTO admin (login, password, firstname, lastname, remember_me_token, remember_me_serial) VALUES
('admin', '$2y$10$8K1p/a0dN/5xS2Z8r3jGdOQvaGbS.nVlkeC5z3gK5iX5hRmVcFdm2', 'System', 'Administrator', 'a1b2c3d4e5f6', 's1e2r3i4a5l6');

INSERT INTO customer (login, password, firstname, lastname, email, remember_me_token, remember_me_serial) VALUES
('customer1', '$2y$10$vD7klLF9G4gHBq0A0lXzKO8QLQZ5N1F3EwzFxhJGmGz4/TcKxLemu', 'John', 'Doe', 'john@example.com', NULL, NULL),
('customer2', '$2y$10$vD7klLF9G4gHBq0A0lXzKO8QLQZ5N1F3EwzFxhJGmGz4/TcKxLemu', 'Jane', 'Smith', 'jane@example.com', NULL, NULL);

INSERT INTO admin_notes (admin_id, title, content) VALUES
(1, 'System Configuration', 'Remember to update SSL certificates before Q2.'),
(1, 'Credentials', 'FLAG_PLACEHOLDER'),
(1, 'Deployment Notes', 'Production server is running StoreCMS 2.1.2 on PHP 8.2.');

INSERT INTO orders (customer_id, ref, status_id, total_amount) VALUES
(1, 'ORD-20240115-001', 4, 149.99),
(1, 'ORD-20240203-002', 4, 89.50),
(2, 'ORD-20240220-003', 2, 245.00);
