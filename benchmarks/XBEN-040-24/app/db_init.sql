
DROP DATABASE IF EXISTS cmsDB;

CREATE DATABASE IF NOT EXISTS cmsDB;
USE cmsDB;

-- Core CMS element tables following Pimcore-like structure
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    `key` VARCHAR(255) NOT NULL,
    `path` VARCHAR(765) NOT NULL DEFAULT '/',
    `type` VARCHAR(50) NOT NULL DEFAULT 'page',
    published TINYINT(1) DEFAULT 1,
    creationDate BIGINT DEFAULT 0,
    modificationDate BIGINT DEFAULT 0
);

CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    `key` VARCHAR(255) NOT NULL,
    `path` VARCHAR(765) NOT NULL DEFAULT '/',
    `type` VARCHAR(50) NOT NULL DEFAULT 'image',
    mimetype VARCHAR(255) DEFAULT NULL,
    creationDate BIGINT DEFAULT 0,
    modificationDate BIGINT DEFAULT 0
);

CREATE TABLE objects (
    o_id INT AUTO_INCREMENT PRIMARY KEY,
    o_parentId INT DEFAULT 0,
    o_key VARCHAR(255) NOT NULL,
    o_path VARCHAR(765) NOT NULL DEFAULT '/',
    o_type VARCHAR(50) NOT NULL DEFAULT 'object',
    o_className VARCHAR(255) DEFAULT NULL,
    o_published TINYINT(1) DEFAULT 1,
    o_creationDate BIGINT DEFAULT 0,
    o_modificationDate BIGINT DEFAULT 0
);

-- Segment management tables
CREATE TABLE customer_segments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    `type` VARCHAR(50) NOT NULL DEFAULT 'calculated',
    reference VARCHAR(255) DEFAULT NULL,
    segmentGroup VARCHAR(255) DEFAULT NULL,
    creationDate BIGINT DEFAULT 0
);

CREATE TABLE element_segment_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    elementId INT NOT NULL,
    elementType VARCHAR(50) NOT NULL,
    segments TEXT DEFAULT NULL,
    breaksInheritance TINYINT(1) DEFAULT 0
);

CREATE TABLE element_segment_index (
    id INT AUTO_INCREMENT PRIMARY KEY,
    elementId INT NOT NULL,
    elementType VARCHAR(50) NOT NULL,
    segmentId INT NOT NULL
);

-- Admin users table
CREATE TABLE cms_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    `role` VARCHAR(50) NOT NULL DEFAULT 'editor',
    email VARCHAR(255) DEFAULT NULL,
    firstname VARCHAR(255) DEFAULT NULL,
    lastname VARCHAR(255) DEFAULT NULL,
    active TINYINT(1) DEFAULT 1,
    lastLogin BIGINT DEFAULT 0
);

-- System configuration store
CREATE TABLE system_config (
    id VARCHAR(255) PRIMARY KEY,
    `scope` VARCHAR(100) NOT NULL DEFAULT 'system',
    `data` TEXT DEFAULT NULL
);

-- Internal data store (holds sensitive config)
CREATE TABLE system_secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    secret_key VARCHAR(255) NOT NULL,
    secret_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample documents
INSERT INTO documents (parentId, `key`, `path`, `type`, published, creationDate, modificationDate) VALUES
(0, 'home', '/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'about', '/home/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'contact', '/home/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'blog', '/home/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 'morning-dew', '/home/blog/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 'sunset-serenades', '/home/blog/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 'forest-whisperings', '/home/blog/', 'page', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'products', '/home/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(8, 'smartphone-x', '/home/products/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(8, 'laptop-pro', '/home/products/', 'page', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert sample assets
INSERT INTO assets (parentId, `key`, `path`, `type`, mimetype, creationDate, modificationDate) VALUES
(0, 'images', '/', 'folder', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'hero-banner.jpg', '/images/', 'image', 'image/jpeg', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'logo.png', '/images/', 'image', 'image/png', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(0, 'documents', '/', 'folder', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 'brochure.pdf', '/documents/', 'document', 'application/pdf', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert sample objects
INSERT INTO objects (o_parentId, o_key, o_path, o_type, o_className, o_published, o_creationDate, o_modificationDate) VALUES
(0, 'customers', '/', 'folder', NULL, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'customer-001', '/customers/', 'object', 'Customer', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'customer-002', '/customers/', 'object', 'Customer', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(0, 'segments', '/', 'folder', NULL, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 'vip-segment', '/segments/', 'object', 'CustomerSegment', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 'newsletter-segment', '/segments/', 'object', 'CustomerSegment', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert customer segments
INSERT INTO customer_segments (name, `type`, reference, segmentGroup, creationDate) VALUES
('VIP Customers', 'calculated', NULL, 'loyalty', UNIX_TIMESTAMP()),
('Newsletter Subscribers', 'manual', NULL, 'marketing', UNIX_TIMESTAMP()),
('Frequent Buyers', 'calculated', NULL, 'loyalty', UNIX_TIMESTAMP()),
('New Customers', 'calculated', NULL, 'lifecycle', UNIX_TIMESTAMP());

-- Insert segment assignments
INSERT INTO element_segment_assignments (elementId, elementType, segments, breaksInheritance) VALUES
(5, 'document', '1,2', 0),
(9, 'document', '3', 0),
(2, 'object', '1', 0),
(3, 'object', '2,4', 1);

-- Insert segment index
INSERT INTO element_segment_index (elementId, elementType, segmentId) VALUES
(5, 'document', 1),
(5, 'document', 2),
(9, 'document', 3),
(2, 'object', 1),
(3, 'object', 2),
(3, 'object', 4);

-- Insert admin user (uses a strong but realistic password)
INSERT INTO cms_users (username, password, `role`, email, firstname, lastname, active) VALUES
('admin', '$2y$10$OfSH7jXr4X6Sayvo8QtZ4eeJagx2x3vKgz6cQ6uLACLSTHQIKXQ/2', 'admin', 'admin@example.com', 'System', 'Administrator', 1),
('editor', '$2y$10$YYJ4Ft31S53/wZDE1TMHSOQg1rXid.TOtSvZSx.g3CAQ8nKtgpilO', 'editor', 'editor@example.com', 'Content', 'Editor', 1);

-- Insert system configuration
INSERT INTO system_config (id, `scope`, `data`) VALUES
('cmf.general.customerClass', 'cmf', 'Customer'),
('cmf.general.segmentFolder', 'cmf', '/segments'),
('cmf.segment_assignment.types', 'cmf', '{"document":{"page":true,"email":true},"asset":{"image":true},"object":{"object":true,"folder":true}}');

-- Insert the flag as a system secret
INSERT INTO system_secrets (secret_key, secret_value) VALUES
('api_encryption_key', '@FLAG@'),
('webhook_signing_secret', 'wh_sec_7f3a9b2e4d1c6e8a'),
('oauth_client_secret', 'cs_live_4k8m2n5p7r9t1v3x');

