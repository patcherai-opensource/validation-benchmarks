CREATE DATABASE IF NOT EXISTS contentforge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE contentforge;

CREATE TABLE IF NOT EXISTS cms_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    legacy_hash VARCHAR(64) DEFAULT NULL,
    role ENUM('admin', 'editor', 'viewer') NOT NULL DEFAULT 'editor',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL,
    INDEX idx_username (username),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cms_pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    content TEXT,
    status ENUM('published', 'draft', 'archived') NOT NULL DEFAULT 'draft',
    author_id INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES cms_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cms_sessions (
    id VARCHAR(128) PRIMARY KEY,
    user_id INT NOT NULL,
    data TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES cms_users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cms_audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(64) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_action (action),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO cms_users (username, password, legacy_hash, role, is_active) VALUES
('admin', '$2y$10$/FShDM.2xCFNoVJT6SC2BO3woODnwCjbf6KfvK7DzVtOY4IEnvHXu', 'a7b9c3d2e1f04a5b8c6d7e8f9a0b1c2d', 'admin', 1);

INSERT INTO cms_users (username, password, legacy_hash, role, is_active) VALUES
('editor', '$1$xR4f2q$AynK0K7U8K6J.7qfu13yl/', NULL, 'editor', 1);

INSERT INTO cms_users (username, password, legacy_hash, role, is_active) VALUES
('testuser', '$1$ab3Kqw$wF0PgZdT7I5mYkXrZ8YRt/', NULL, 'viewer', 0);

-- Sample content pages
INSERT INTO cms_pages (title, slug, content, status, author_id) VALUES
('Welcome to ContentForge', 'welcome', 'Welcome to our content management platform.', 'published', 1),
('Getting Started Guide', 'getting-started', 'This guide will help you get started with ContentForge CMS.', 'published', 1),
('API Documentation', 'api-docs', 'ContentForge provides a RESTful API for content management.', 'draft', 2);

GRANT ALL PRIVILEGES ON contentforge.* TO 'cfadmin'@'%';
FLUSH PRIVILEGES;
