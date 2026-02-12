DROP DATABASE IF EXISTS pimcore;
CREATE DATABASE IF NOT EXISTS pimcore;
USE pimcore;

-- Ensure application user has access
GRANT ALL PRIVILEGES ON pimcore.* TO 'user'@'%';
FLUSH PRIVILEGES;

-- Core Pimcore tables
CREATE TABLE objects (
    o_id INT AUTO_INCREMENT PRIMARY KEY,
    o_parentId INT DEFAULT 0,
    o_type VARCHAR(20) DEFAULT 'object',
    o_key VARCHAR(255) NOT NULL,
    o_path VARCHAR(765) DEFAULT '/',
    o_classId VARCHAR(50) DEFAULT NULL,
    o_className VARCHAR(255) DEFAULT NULL,
    o_creationDate INT UNSIGNED DEFAULT NULL,
    o_modificationDate INT UNSIGNED DEFAULT NULL,
    o_userOwner INT UNSIGNED DEFAULT 0,
    o_userModification INT UNSIGNED DEFAULT 0,
    o_published TINYINT(1) DEFAULT 1
);

CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    type VARCHAR(20) DEFAULT 'page',
    `key` VARCHAR(255) NOT NULL,
    path VARCHAR(765) DEFAULT '/',
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    userOwner INT UNSIGNED DEFAULT 0,
    userModification INT UNSIGNED DEFAULT 0,
    published TINYINT(1) DEFAULT 1
);

CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    type VARCHAR(20) DEFAULT 'folder',
    filename VARCHAR(255) NOT NULL,
    path VARCHAR(765) DEFAULT '/',
    mimetype VARCHAR(255) DEFAULT NULL,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    userOwner INT UNSIGNED DEFAULT 0,
    userModification INT UNSIGNED DEFAULT 0
);

-- Customer Management Framework tables
CREATE TABLE plugin_cmf_segment_assignment (
    elementId INT NOT NULL,
    elementType VARCHAR(20) NOT NULL,
    segmentId INT NOT NULL,
    breaksInheritance TINYINT(1) DEFAULT 0,
    PRIMARY KEY (elementId, elementType, segmentId)
);

CREATE TABLE plugin_cmf_customer_segments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    reference VARCHAR(255) DEFAULT NULL,
    `group` VARCHAR(255) DEFAULT NULL,
    calculated TINYINT(1) DEFAULT 0,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    useAsTargetGroup TINYINT(1) DEFAULT 0
);

CREATE TABLE plugin_cmf_customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customerId VARCHAR(255) NOT NULL,
    email VARCHAR(255) DEFAULT NULL,
    firstname VARCHAR(255) DEFAULT NULL,
    lastname VARCHAR(255) DEFAULT NULL,
    `active` TINYINT(1) DEFAULT 1,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL
);

CREATE TABLE plugin_cmf_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customerId INT DEFAULT NULL,
    activityDate INT UNSIGNED DEFAULT NULL,
    type VARCHAR(255) DEFAULT NULL,
    implementationClass VARCHAR(255) DEFAULT NULL,
    attributes TEXT DEFAULT NULL,
    md5 VARCHAR(32) DEFAULT NULL,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL
);

-- Admin users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    admin TINYINT(1) DEFAULT 0,
    active TINYINT(1) DEFAULT 1,
    lastLogin INT UNSIGNED DEFAULT NULL,
    apiKey VARCHAR(255) DEFAULT NULL
);

-- System configuration
CREATE TABLE system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scope VARCHAR(255) NOT NULL,
    `key` VARCHAR(255) NOT NULL,
    value TEXT DEFAULT NULL
);

-- Insert sample data for objects
INSERT INTO objects (o_id, o_parentId, o_type, o_key, o_path, o_classId, o_className, o_creationDate, o_modificationDate) VALUES
(1, 0, 'folder', 'customers', '/', NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 1, 'object', 'john-doe', '/customers/', 'CU', 'Customer', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 1, 'object', 'jane-smith', '/customers/', 'CU', 'Customer', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 0, 'folder', 'segments', '/', NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(5, 4, 'object', 'premium-users', '/segments/', 'CS', 'CustomerSegment', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(6, 4, 'object', 'newsletter-subscribers', '/segments/', 'CS', 'CustomerSegment', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(7, 1, 'object', 'bob-wilson', '/customers/', 'CU', 'Customer', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(8, 4, 'object', 'vip-members', '/segments/', 'CS', 'CustomerSegment', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert sample documents
INSERT INTO documents (id, parentId, type, `key`, path, creationDate, modificationDate) VALUES
(1, 0, 'page', 'home', '/', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 1, 'page', 'about', '/', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 1, 'page', 'contact', '/', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 0, 'folder', 'emails', '/', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(5, 4, 'email', 'newsletter-template', '/emails/', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert sample assets
INSERT INTO assets (id, parentId, type, filename, path, mimetype, creationDate, modificationDate) VALUES
(1, 0, 'folder', 'images', '/', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 1, 'image', 'logo.png', '/images/', 'image/png', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 1, 'image', 'banner.jpg', '/images/', 'image/jpeg', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert customer segments
INSERT INTO plugin_cmf_customer_segments (id, name, reference, `group`, calculated, creationDate, modificationDate, useAsTargetGroup) VALUES
(1, 'Premium Users', 'premium-users', 'Loyalty', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(2, 'Newsletter Subscribers', 'newsletter-subs', 'Communication', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0),
(3, 'VIP Members', 'vip-members', 'Loyalty', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(4, 'New Customers', 'new-customers', 'Lifecycle', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0),
(5, 'Inactive Users', 'inactive-users', 'Lifecycle', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0);

-- Insert segment assignments
INSERT INTO plugin_cmf_segment_assignment (elementId, elementType, segmentId, breaksInheritance) VALUES
(2, 'object', 1, 0),
(2, 'object', 2, 0),
(3, 'object', 1, 0),
(3, 'object', 3, 1),
(7, 'object', 2, 0),
(7, 'object', 4, 0),
(1, 'document', 2, 0),
(5, 'document', 1, 0);

-- Insert customers
INSERT INTO plugin_cmf_customers (id, customerId, email, firstname, lastname, active, creationDate, modificationDate) VALUES
(1, 'CU-001', 'john.doe@example.com', 'John', 'Doe', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 'CU-002', 'jane.smith@example.com', 'Jane', 'Smith', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 'CU-003', 'bob.wilson@example.com', 'Bob', 'Wilson', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert activities
INSERT INTO plugin_cmf_activities (customerId, activityDate, type, implementationClass, attributes, md5, creationDate, modificationDate) VALUES
(1, UNIX_TIMESTAMP(), 'Login', 'CustomerManagementFrameworkBundle\\Model\\Activity\\DefaultActivity', '{"source":"web"}', MD5('login-1'), UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, UNIX_TIMESTAMP(), 'Purchase', 'CustomerManagementFrameworkBundle\\Model\\Activity\\DefaultActivity', '{"amount":"99.99"}', MD5('purchase-2'), UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, UNIX_TIMESTAMP(), 'Newsletter Signup', 'CustomerManagementFrameworkBundle\\Model\\Activity\\DefaultActivity', '{"channel":"email"}', MD5('newsletter-3'), UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert admin user
INSERT INTO users (username, password, name, email, admin, active, lastLogin) VALUES
('admin', '$ADMIN_HASH$', 'System Administrator', 'admin@pimcore.example.com', 1, 1, UNIX_TIMESTAMP());

-- Create views for API compatibility (singular form aliases)
CREATE VIEW object AS SELECT o_id, o_parentId, o_type, o_key, o_path FROM objects;
CREATE VIEW document AS SELECT id, parentId, type, `key`, path FROM documents;
CREATE VIEW asset AS SELECT id, parentId, type, filename, path FROM assets;

-- System configuration - flag stored here
INSERT INTO system_config (scope, `key`, value) VALUES
('cmf', 'general.customerClassName', 'Customer'),
('cmf', 'general.segmentFolderPath', '/segments'),
('cmf', 'general.customerFolderPath', '/customers'),
('system', 'general.timezone', 'Europe/Berlin'),
('system', 'general.language', 'en'),
('system', 'secret.api_key', '@FLAG@');
