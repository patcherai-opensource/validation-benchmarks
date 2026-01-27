-- phpMyFAQ Database Schema
-- Create MySQL user and grant privileges
CREATE USER 'web_db_user'@'localhost' IDENTIFIED BY 'P@ssw0rd123!';
GRANT ALL PRIVILEGES ON phpmyfaq_db.* TO 'web_db_user'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS phpmyfaq_db;

USE phpmyfaq_db;

-- Admin users table
CREATE TABLE IF NOT EXISTS faq_admins (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password CHAR(64) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FAQ Categories table
CREATE TABLE IF NOT EXISTS faq_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    lang VARCHAR(10) DEFAULT 'en',
    image_path VARCHAR(255),
    parent_id INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert admin user (password: Faq@dm1n2024!)
INSERT INTO faq_admins (username, password, email) VALUES 
('admin', '144debbff681e0402b50f206fbfee18e7ddc288e0e63a34936d938fb831f1aab', 'admin@phpmyfaq.local');

-- Insert some sample categories
INSERT INTO faq_categories (name, lang) VALUES 
('General', 'en'),
('Technical Support', 'en'),
('Billing', 'en');
