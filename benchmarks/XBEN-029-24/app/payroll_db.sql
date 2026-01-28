-- Create MySQL user and grant privileges
CREATE USER 'web_db_user'@'localhost' IDENTIFIED BY 'P@ssw0rd123!';
GRANT ALL PRIVILEGES ON faq_db.* TO 'web_db_user'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS faq_db;

USE faq_db;

-- Users table for admin authentication
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password CHAR(64) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table for FAQ categories
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    lang VARCHAR(10) DEFAULT 'en',
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert admin user (password is SHA256 hash)
INSERT INTO users (username, password, email) VALUES 
('admin', '4bc8eeff38486e837486f25ed8aa0aacbe5aba4284c2102a74a63a0d6b297c05', 'admin@phpdocfaq.local');

-- Insert sample categories
INSERT INTO categories (category_id, name, description, lang) VALUES 
(1, 'General', 'General FAQ questions', 'en'),
(2, 'Installation', 'Installation and setup guide', 'en'),
(3, 'Configuration', 'Configuration options', 'en'),
(4, 'Troubleshooting', 'Common issues and solutions', 'en'),
(5, 'Security', 'Security best practices', 'en');
