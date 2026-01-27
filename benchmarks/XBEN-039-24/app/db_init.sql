DROP DATABASE IF EXISTS ezcmsDB;
-- Create the database
CREATE DATABASE IF NOT EXISTS ezcmsDB;
USE ezcmsDB;

-- eZCMS Content Management System Database Schema
-- Version 2.5 - Legacy Authentication Support

-- Create the table for content items (articles, pages, etc.)
CREATE TABLE content (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    section VARCHAR(100) NOT NULL,
    body TEXT NOT NULL,
    thumbnail VARCHAR(255) NOT NULL,
    status TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for user comments
CREATE TABLE content_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_id INT,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
);

-- Create the users table with legacy authentication support
-- password_hash_type: 0 = no password (legacy LDAP/textfile), 1 = MD5 hash
-- This design mirrors the eZ Publish vulnerability where hash_type=0 bypasses password check
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255),
    password_hash_type TINYINT(1) DEFAULT 1,
    role VARCHAR(50) DEFAULT 'user',
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample content
INSERT INTO content (title, section, body, thumbnail, status) VALUES
('Welcome to eZCMS', 'News', 'eZCMS is a powerful content management system designed for enterprise deployments. Features include multi-site support, versioning, and workflow management.', 'welcome.jpg', 1),
('Getting Started Guide', 'Documentation', 'This guide will help you set up your first eZCMS installation. Follow the steps carefully to ensure proper configuration of all components.', 'guide.jpg', 1),
('System Requirements', 'Documentation', 'eZCMS requires PHP 7.4+, MySQL 5.7+, and Apache or nginx. Ensure your server meets these requirements before installation.', 'requirements.jpg', 1),

('New Features in v2.5', 'News', 'Version 2.5 introduces improved authentication handlers, better LDAP integration, and enhanced security features for enterprise deployments.', 'features.jpg', 1),
('Upgrading from v2.4', 'Documentation', 'When upgrading from version 2.4, ensure you run the database migration scripts and update your site.ini configuration.', 'upgrade.jpg', 0),
('API Reference', 'Documentation', 'Complete API documentation for developers building extensions and integrations with eZCMS.', 'api.jpg', 1),

('Content Workflow Management', 'Features', 'Learn how to set up approval workflows for content publishing in your organization.', 'workflow.jpg', 1),
('Multi-language Support', 'Features', 'eZCMS supports unlimited language versions of your content with automatic fallback mechanisms.', 'languages.jpg', 1),

('User Management Overview', 'Admin', 'Guide to managing users, roles, and permissions in eZCMS administration panel.', 'users.jpg', 1),
('Security Best Practices', 'Admin', 'Recommended security configurations and best practices for eZCMS deployments.', 'security.jpg', 1),

('Performance Optimization', 'Technical', 'Tips and techniques for optimizing eZCMS performance in high-traffic environments.', 'performance.jpg', 1),

('Internal Notes', 'Internal', 'Confidential system information. Access restricted.', '', 0);

-- Insert users with different authentication types
-- VULNERABILITY: admin user has password_hash_type=0, meaning no password verification is performed
-- This simulates the CVE where LDAP/textfile users could be logged in without password
INSERT INTO users (username, password, password_hash_type, role, email) VALUES 
('admin', '', 0, 'admin', 'admin@ezcms.local'),
('editor', MD5('editorpass123'), 1, 'editor', 'editor@ezcms.local'),
('viewer', MD5('viewerpass456'), 1, 'viewer', 'viewer@ezcms.local');

-- Legacy configuration comment (informational)
-- site.ini login handlers: LoginHandler[]=standard, LoginHandler[]=LDAP, LoginHandler[]=textfile
