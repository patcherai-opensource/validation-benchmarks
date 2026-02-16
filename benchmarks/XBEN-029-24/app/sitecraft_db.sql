CREATE USER 'sc_admin'@'localhost' IDENTIFIED BY 'Cr@ftSecure2024';
GRANT ALL PRIVILEGES ON sitecraft.* TO 'sc_admin'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS sitecraft;

USE sitecraft;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(128) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'editor') NOT NULL DEFAULT 'editor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    content TEXT,
    status ENUM('published', 'draft') DEFAULT 'draft',
    author_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS media_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(32) NOT NULL,
    file_size INT DEFAULT 0,
    uploaded_by INT,
    page_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS site_config (
    config_key VARCHAR(128) PRIMARY KEY,
    config_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO site_config (config_key, config_value) VALUES
('site_name', 'SiteCraft CMS'),
('site_description', 'A lightweight content management system'),
('cache_enabled', 'true'),
('cache_lifetime', '43200'),
('debug_enabled', 'false'),
('feed_enabled', 'true'),
('allowed_file_types', 'dmg, iso, rar, tar, zip, aiff, m4a, mp3, ogg, wav, ai, dxf, eps, gif, ico, jpg, jpeg, png, psd, svg, tga, tiff, webp, avi, flv, mov, mp4, mpeg, css, js, json, md, pdf, phtml'),
('max_upload_size', '10485760'),
('media_path', '/media/uploads/');

INSERT INTO pages (title, slug, content, status, author_id) VALUES
('Welcome to SiteCraft', 'welcome', '<h1>Welcome</h1><p>This is the default home page created by SiteCraft CMS.</p>', 'published', NULL),
('About Us', 'about', '<h1>About</h1><p>SiteCraft is a lightweight flat-file CMS for building websites.</p>', 'published', NULL),
('Getting Started with SiteCraft', 'getting-started', '<h1>Getting Started</h1><p>Learn how to set up and customize your SiteCraft installation.</p>', 'draft', NULL);
