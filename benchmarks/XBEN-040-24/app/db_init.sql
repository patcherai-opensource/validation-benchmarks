
DROP DATABASE IF EXISTS blogDB;

-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the table for subsites
CREATE TABLE subsites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    theme VARCHAR(100) NOT NULL,
    is_default TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for groups (maps to subsites)
CREATE TABLE site_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL,
    subsite_id INT,
    access_all_subsites TINYINT(1) DEFAULT 0,
    permissions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subsite_id) REFERENCES subsites(id) ON DELETE SET NULL
);

-- Create the table for system admins
CREATE TABLE cms_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'admin'
);

-- Create a schema registry table (simulating SilverStripe's schema system)
CREATE TABLE schema_registry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    is_active TINYINT(1) DEFAULT 1
);

-- Insert sample subsites
INSERT INTO subsites (title, domain, theme, is_default) VALUES
('Main Site', 'www.example.com', 'corporate', 1),
('Marketing Portal', 'marketing.example.com', 'modern', 0),
('Developer Hub', 'dev.example.com', 'minimal', 0),
('Customer Support', 'support.example.com', 'friendly', 0),
('Partner Network', 'partners.example.com', 'professional', 0);

-- Insert sample groups
INSERT INTO site_groups (group_name, subsite_id, access_all_subsites, permissions) VALUES
('Administrators', 1, 1, 'ADMIN,EDIT,DELETE,CREATE'),
('Content Editors', 1, 0, 'EDIT,CREATE'),
('Marketing Team', 2, 0, 'EDIT,CREATE,PUBLISH'),
('Developers', 3, 0, 'ADMIN,EDIT,DELETE,CREATE'),
('Support Staff', 4, 0, 'EDIT,VIEW'),
('Partner Managers', 5, 0, 'VIEW,EDIT');

-- Insert schema registry entries
INSERT INTO schema_registry (class_name, table_name) VALUES
('SilverStripe\\Security\\Group', 'site_groups'),
('SilverStripe\\Subsites\\Model\\Subsite', 'subsites'),
('SilverStripe\\Security\\Member', 'cms_admins');

-- Insert CMS admin credentials
INSERT INTO cms_admins (username, password, email, role) VALUES ('siteadmin', 'Str0ngP@ssw0rd_CMS!', 'admin@example.com', 'super_admin');

