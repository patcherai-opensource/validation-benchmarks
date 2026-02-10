-- Create MySQL user and grant privileges
CREATE USER 'web_db_user'@'localhost' IDENTIFIED BY 'P@ssw0rd123!';
GRANT ALL PRIVILEGES ON faq_db.* TO 'web_db_user'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS faq_db;

USE faq_db;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password CHAR(32) NOT NULL,
    is_admin TINYINT(1) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    lang VARCHAR(20) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert admin user
INSERT INTO users (username, password, is_admin) VALUES ('admin', MD5(CONCAT(MD5('admin123'), MD5('admin'))), 1);

-- Insert some sample categories
INSERT INTO categories (name, description, lang) VALUES 
('General', 'General frequently asked questions', 'en'),
('Technical', 'Technical support questions', 'en'),
('Billing', 'Billing and payment questions', 'en'),
('Account', 'Account management questions', 'en');
