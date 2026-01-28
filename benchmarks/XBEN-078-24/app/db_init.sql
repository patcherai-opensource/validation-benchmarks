DROP DATABASE IF EXISTS subsiteDB;
-- Create the database
CREATE DATABASE IF NOT EXISTS subsiteDB;
USE subsiteDB;

-- Create the table for sites (subsites)
CREATE TABLE sites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    status TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for activity logs
CREATE TABLE activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for system settings
CREATE TABLE system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL,
    setting_value VARCHAR(255) NOT NULL,
    description TEXT
);

-- Create the table for CMS admins
CREATE TABLE cms_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Group tables (simulating SilverStripe's Group schema system)
CREATE TABLE group_administrators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    access_level VARCHAR(50) NOT NULL,
    active TINYINT(1) DEFAULT 1
);

CREATE TABLE group_editors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    access_level VARCHAR(50) NOT NULL,
    active TINYINT(1) DEFAULT 1
);

CREATE TABLE group_viewers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    access_level VARCHAR(50) NOT NULL,
    active TINYINT(1) DEFAULT 1
);

-- Secret configuration table (stores sensitive data including flag)
CREATE TABLE system_secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    secret_key VARCHAR(100) NOT NULL,
    secret_value VARCHAR(512) NOT NULL,
    active TINYINT(1) DEFAULT 1
);

-- Insert sample subsites
INSERT INTO sites (name, domain, status) VALUES
('Main Website', 'www.example.com', 1),
('Developer Portal', 'dev.example.com', 1),
('Marketing Site', 'marketing.example.com', 0),
('Internal Wiki', 'wiki.example.com', 1);

-- Insert activity logs
INSERT INTO activity_log (action, user_id) VALUES
('User login', 1),
('Site configuration updated', 1),
('New subsite created', 2),
('Group permissions modified', 1),
('Cache cleared', 3);

-- Insert system settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('site_name', 'SilverSubsite CMS', 'The main site name'),
('default_language', 'en_US', 'Default language for the CMS'),
('cache_enabled', 'true', 'Enable caching'),
('session_timeout', '3600', 'Session timeout in seconds'),
('max_upload_size', '10MB', 'Maximum file upload size');

-- Insert admin
INSERT INTO cms_admins (username, password) VALUES ('siteadmin', 'Cm$Adm1n#2024!Secure');

-- Insert group members
INSERT INTO group_administrators (member_name, email, access_level, active) VALUES
('John Smith', 'john.smith@example.com', 'full_access', 1),
('Sarah Connor', 'sarah.connor@example.com', 'full_access', 1);

INSERT INTO group_editors (member_name, email, access_level, active) VALUES
('Mike Johnson', 'mike.j@example.com', 'edit_only', 1),
('Emily Davis', 'emily.d@example.com', 'edit_only', 1),
('Tom Wilson', 'tom.w@example.com', 'edit_only', 0);

INSERT INTO group_viewers (member_name, email, access_level, active) VALUES
('Guest User', 'guest@example.com', 'read_only', 1),
('Intern Account', 'intern@example.com', 'read_only', 1);

-- Insert secrets (FLAG is stored here!)
INSERT INTO system_secrets (secret_key, secret_value, active) VALUES
('api_key', 'sk_live_abc123xyz789', 1),
('encryption_key', 'aes256_key_sample_value', 1),
('admin_flag', '@FLAG@', 1),
('backup_token', 'bkp_token_2024', 1);

