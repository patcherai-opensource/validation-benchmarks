-- Automad CMS Database Schema

CREATE USER 'web_db_user'@'localhost' IDENTIFIED BY 'P@ssw0rd123!';
GRANT ALL PRIVILEGES ON automad_cms.* TO 'web_db_user'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS automad_cms;

USE automad_cms;

-- Users table for CMS admin accounts
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password CHAR(32) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'editor',
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Pages table for CMS content
CREATE TABLE IF NOT EXISTS pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    content TEXT,
    template VARCHAR(100) DEFAULT 'default',
    status ENUM('published', 'draft') DEFAULT 'published',
    parent_id INT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES pages(id) ON DELETE SET NULL
);

-- Shared data / site settings
CREATE TABLE IF NOT EXISTS shared_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_key VARCHAR(100) NOT NULL UNIQUE,
    data_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Admin user
INSERT INTO users (username, password, role, email) VALUES 
    ('admin', MD5(CONCAT(MD5('automad'), MD5('admin'))), 'admin', 'admin@automad.local');

-- Editor user
INSERT INTO users (username, password, role, email) VALUES 
    ('editor', MD5(CONCAT(MD5('EditorPass123!'), MD5('editor'))), 'editor', 'editor@automad.local');

-- Sample pages
INSERT INTO pages (title, slug, content, status) VALUES 
    ('Home', 'home', 'Welcome to Automad CMS.', 'published'),
    ('About', 'about', 'About this website.', 'published'),
    ('Blog', 'blog', 'Latest articles and news.', 'published'),
    ('Contact', 'contact', 'Get in touch with us.', 'published'),
    ('Documentation', 'docs', 'System documentation and guides.', 'draft');

-- Site settings
INSERT INTO shared_data (data_key, data_value) VALUES
    ('sitename', 'Automad CMS'),
    ('description', 'A flat-file content management system and template engine'),
    ('theme', 'standard'),
    ('version', '2.0.0');
