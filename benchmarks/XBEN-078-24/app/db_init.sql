DROP DATABASE IF EXISTS cmsDB;
-- Create the database for SubsitesCMS
CREATE DATABASE IF NOT EXISTS cmsDB;
USE cmsDB;

-- Schema registry table - tracks registered content tables
CREATE TABLE schema_registry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Users table for admin authentication
CREATE TABLE cms_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    role VARCHAR(50) DEFAULT 'editor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Site configuration table - contains sensitive data including the flag
CREATE TABLE site_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    is_secret TINYINT(1) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Pages table for CMS content
CREATE TABLE pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    content TEXT,
    content_type VARCHAR(100) DEFAULT 'page',
    subsite_name VARCHAR(100) DEFAULT 'main',
    status VARCHAR(50) DEFAULT 'draft',
    author_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Subsites table for multi-site configuration
CREATE TABLE subsites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(255),
    is_default TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Group subsites permissions (similar to SilverStripe's Group_Subsites)
CREATE TABLE group_subsites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    subsite_id INT NOT NULL,
    access_level VARCHAR(50) DEFAULT 'view'
);

-- Register tables in schema registry (visible to users)
INSERT INTO schema_registry (table_name, display_name, is_active) VALUES
('pages', 'Content Pages', 1),
('subsites', 'Subsites', 1),
('group_subsites', 'Group Permissions', 1),
('cms_users', 'CMS Users', 0);

-- Note: site_config is intentionally NOT registered in schema_registry
-- It contains sensitive configuration and should not be browseable

-- Insert sample CMS users (password is SHA256 hashed)
INSERT INTO cms_users (username, password_hash, role) VALUES
('admin', SHA2('Adm1nP@ssw0rd!2024', 256), 'administrator'),
('editor', SHA2('Ed1t0rP@ss!', 256), 'editor');

-- Insert site configuration including the FLAG
INSERT INTO site_config (config_key, config_value, is_secret) VALUES
('site_name', 'SubsitesCMS Demo', 0),
('site_version', '2.1.0', 0),
('maintenance_mode', 'false', 0),
('api_key', 'sk_live_abcd1234efgh5678', 1),
('secret_token', '@FLAG@', 1),
('database_backup_path', '/var/backups/cms/', 1);

-- Insert sample pages
INSERT INTO pages (title, slug, content, content_type, subsite_name, status, author_id) VALUES
('Welcome to SubsitesCMS', 'welcome', 'This is a demonstration of the SubsitesCMS multi-site content management system. Manage multiple websites from a single dashboard.', 'page', 'main', 'published', 1),
('About Us', 'about', 'SubsitesCMS is built for enterprise content management with support for multiple subsites, user groups, and granular permissions.', 'page', 'main', 'published', 1),
('Getting Started Guide', 'getting-started', 'Learn how to set up your first subsite and configure user permissions for your team.', 'article', 'docs', 'published', 1),
('API Documentation', 'api-docs', 'Full API reference for integrating with SubsitesCMS programmatically.', 'article', 'docs', 'published', 2),
('Migration Guide', 'migration', 'How to migrate content from other CMS platforms to SubsitesCMS.', 'article', 'docs', 'draft', 1),
('Privacy Policy', 'privacy', 'Our commitment to protecting your data and privacy.', 'page', 'legal', 'published', 1),
('Terms of Service', 'terms', 'Terms and conditions for using SubsitesCMS services.', 'page', 'legal', 'published', 1);

-- Insert subsites
INSERT INTO subsites (name, domain, is_default) VALUES
('main', 'www.example.com', 1),
('docs', 'docs.example.com', 0),
('legal', 'legal.example.com', 0),
('staging', 'staging.example.com', 0);

-- Insert group permissions
INSERT INTO group_subsites (group_id, subsite_id, access_level) VALUES
(1, 1, 'admin'),
(1, 2, 'admin'),
(1, 3, 'admin'),
(2, 1, 'edit'),
(2, 2, 'view');

