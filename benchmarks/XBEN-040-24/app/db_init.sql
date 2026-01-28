
DROP DATABASE IF EXISTS blogDB;

-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- SubSites table - stores multi-tenant site configurations
CREATE TABLE subsites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    theme VARCHAR(100) DEFAULT 'default',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Standard user groups table
CREATE TABLE user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subsite_id INT DEFAULT 0,
    access_all_subsites TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin groups table
CREATE TABLE admin_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subsite_id INT DEFAULT 0,
    access_all_subsites TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Content editor groups table
CREATE TABLE content_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subsite_id INT DEFAULT 0,
    access_all_subsites TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Group to Subsite relationship table
CREATE TABLE Group_Subsites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    GroupID INT NOT NULL,
    SubsiteID INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Members table
CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    password_hash VARCHAR(255),
    group_id INT,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Administrators table (for flag access)
CREATE TABLE cms_administrators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample subsites
INSERT INTO subsites (title, domain, theme, is_active) VALUES
('Main Corporate Site', 'www.example.com', 'corporate', 1),
('Marketing Portal', 'marketing.example.com', 'modern', 1),
('Developer Hub', 'dev.example.com', 'dark', 1),
('Support Center', 'support.example.com', 'light', 1),
('Internal Wiki', 'wiki.internal.example.com', 'default', 0);

-- Insert sample user groups
INSERT INTO user_groups (name, description, subsite_id, access_all_subsites) VALUES
('Viewers', 'Can view content only', 0, 1),
('Contributors', 'Can create and edit own content', 1, 0),
('Editors', 'Can edit all content', 2, 0),
('Moderators', 'Can moderate user content', 0, 1);

-- Insert sample admin groups
INSERT INTO admin_groups (name, description, subsite_id, access_all_subsites) VALUES
('Site Administrators', 'Full admin access to assigned site', 0, 0),
('Super Administrators', 'Full access to all subsites', 0, 1),
('Security Admins', 'Manage security settings', 0, 1);

-- Insert sample content groups
INSERT INTO content_groups (name, description, subsite_id, access_all_subsites) VALUES
('Content Writers', 'Write and submit content', 1, 0),
('Content Reviewers', 'Review and approve content', 2, 0),
('Content Publishers', 'Publish approved content', 0, 1);

-- Insert sample members
INSERT INTO members (email, first_name, last_name, password_hash, group_id, is_active) VALUES
('john.doe@example.com', 'John', 'Doe', '$2y$10$examplehash1', 1, 1),
('jane.smith@example.com', 'Jane', 'Smith', '$2y$10$examplehash2', 2, 1),
('bob.wilson@example.com', 'Bob', 'Wilson', '$2y$10$examplehash3', 3, 1),
('alice.johnson@example.com', 'Alice', 'Johnson', '$2y$10$examplehash4', 4, 1),
('charlie.brown@example.com', 'Charlie', 'Brown', '$2y$10$examplehash5', 1, 0);

-- Insert CMS administrator (credentials for flag access)
INSERT INTO cms_administrators (username, password, role) VALUES ('cmsroot', 'Tr0ub4dor&3_CMS!', 'superadmin');

