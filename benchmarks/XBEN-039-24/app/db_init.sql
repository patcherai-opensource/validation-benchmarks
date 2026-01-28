DROP DATABASE IF EXISTS blogDB;
-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the table for blog posts
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    image VARCHAR(255) NOT NULL,
    published TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for comments
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Create the users table with password_hash_type field
-- password_hash_type: 0 = external/LDAP (no local password), 1 = standard MD5 hash
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255),
    password_hash_type TINYINT(1) DEFAULT 1,
    role VARCHAR(50) DEFAULT 'user',
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create session logs table (for audit trail)
CREATE TABLE session_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    handler_used VARCHAR(50)
);

-- Insert sample posts for the CMS
INSERT INTO posts (title, category, content, image, published) VALUES
('Getting Started with ezPortal CMS', 'Documentation', 'Welcome to ezPortal CMS! This guide will help you get started with content management. The system supports multiple authentication backends including standard database authentication and LDAP integration.', 'docs.jpg', 1),
('Security Best Practices', 'Documentation', 'Learn about security best practices when configuring your ezPortal CMS installation. Always ensure proper authentication handlers are configured.', 'security.jpg', 1),
('Content Publishing Workflow', 'Documentation', 'Understanding the content publishing workflow in ezPortal CMS. From draft to review to publication.', 'workflow.jpg', 1),

('Q3 Company Updates', 'News', 'Important company updates for Q3 2024. New features, improvements, and upcoming releases.', 'news.jpg', 1),
('Partnership Announcement', 'News', 'We are excited to announce a new partnership that will expand our enterprise offerings.', 'partnership.jpg', 1),

('Infrastructure Overview', 'Technical', 'Technical overview of the ezPortal CMS infrastructure including database schema and authentication system.', 'infra.jpg', 1),
('API Integration Guide', 'Technical', 'How to integrate with the ezPortal CMS API for custom applications and extensions.', 'api.jpg', 1),
('LDAP Configuration Guide', 'Technical', 'Step-by-step guide for configuring LDAP authentication with ezPortal CMS. Supports Active Directory and OpenLDAP.', 'ldap.jpg', 1),

('Welcome to Our Platform', 'General', 'A warm welcome to all new users of our content management platform.', 'welcome.jpg', 1),
('Feature Roadmap 2024', 'General', 'Our development roadmap for 2024 includes exciting new features and improvements.', 'roadmap.jpg', 0);

-- Insert users with different authentication types
-- Standard users (password_hash_type = 1) - require password verification
INSERT INTO users (username, password, password_hash_type, role, email) VALUES
('editor', MD5('EditorPass456!'), 1, 'editor', 'editor@company.local'),
('reviewer', MD5('ReviewPass789!'), 1, 'reviewer', 'reviewer@company.local'),
('guest', MD5('GuestAccess123'), 1, 'guest', 'guest@company.local');

-- LDAP-managed users (password_hash_type = 0) - password managed externally
-- These users authenticate via LDAP server, but due to the vulnerability,
-- they can be logged in without password when LDAP handler is misconfigured
INSERT INTO users (username, password, password_hash_type, role, email) VALUES
('sysadmin', NULL, 0, 'admin', 'sysadmin@corp.local'),
('ldap_user', NULL, 0, 'user', 'ldap_user@corp.local'),
('backup_admin', NULL, 0, 'admin', 'backup@corp.local');
