USE pimcore;

-- Core Pimcore tables

CREATE TABLE objects (
    o_id INT AUTO_INCREMENT PRIMARY KEY,
    o_parentId INT DEFAULT 0,
    o_type VARCHAR(20) NOT NULL DEFAULT 'object',
    o_key VARCHAR(255) NOT NULL,
    o_path VARCHAR(765) DEFAULT '/',
    o_classId VARCHAR(50) DEFAULT NULL,
    o_className VARCHAR(255) DEFAULT NULL,
    o_creationDate INT UNSIGNED DEFAULT NULL,
    o_modificationDate INT UNSIGNED DEFAULT NULL,
    o_userOwner INT UNSIGNED DEFAULT NULL,
    o_userModification INT UNSIGNED DEFAULT NULL,
    INDEX idx_parentId (o_parentId),
    INDEX idx_classId (o_classId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    type VARCHAR(20) NOT NULL DEFAULT 'page',
    `key` VARCHAR(255) NOT NULL,
    path VARCHAR(765) DEFAULT '/',
    published TINYINT(1) DEFAULT 1,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    userOwner INT UNSIGNED DEFAULT NULL,
    userModification INT UNSIGNED DEFAULT NULL,
    INDEX idx_parentId (parentId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    type VARCHAR(20) NOT NULL DEFAULT 'folder',
    filename VARCHAR(255) NOT NULL,
    path VARCHAR(765) DEFAULT '/',
    mimetype VARCHAR(255) DEFAULT NULL,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    userOwner INT UNSIGNED DEFAULT NULL,
    userModification INT UNSIGNED DEFAULT NULL,
    INDEX idx_parentId (parentId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Customer management framework tables

CREATE TABLE plugin_cmf_segment_assignment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    elementId INT NOT NULL,
    elementType VARCHAR(20) NOT NULL DEFAULT 'object',
    segmentId INT NOT NULL,
    breaksInheritance TINYINT(1) DEFAULT 0,
    INDEX idx_element (elementId, elementType),
    INDEX idx_segment (segmentId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE plugin_cmf_customer_segments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    `group` VARCHAR(255) DEFAULT NULL,
    reference VARCHAR(255) DEFAULT NULL,
    calculated TINYINT(1) DEFAULT 0,
    creationDate INT UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE plugin_cmf_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customerId INT DEFAULT NULL,
    activityDate DATETIME DEFAULT NULL,
    type VARCHAR(255) DEFAULT NULL,
    implementationClass VARCHAR(255) DEFAULT NULL,
    attributes TEXT DEFAULT NULL,
    md5 VARCHAR(32) DEFAULT NULL,
    creationDate DATETIME DEFAULT NULL,
    modificationDate DATETIME DEFAULT NULL,
    INDEX idx_customer (customerId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE plugin_cmf_action_trigger_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    active TINYINT(1) DEFAULT 0,
    `trigger` TEXT DEFAULT NULL,
    `condition` TEXT DEFAULT NULL,
    `action` TEXT DEFAULT NULL,
    creationDate INT UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Admin users table (Pimcore admin users)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    admin TINYINT(1) DEFAULT 0,
    active TINYINT(1) DEFAULT 1,
    language VARCHAR(10) DEFAULT 'en',
    lastLogin INT UNSIGNED DEFAULT NULL,
    apiKey VARCHAR(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- System configuration (sensitive data)
CREATE TABLE system_configuration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL,
    config_value TEXT NOT NULL,
    scope VARCHAR(50) DEFAULT 'system',
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    INDEX idx_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample data

-- Objects (customers, segments, etc.)
INSERT INTO objects (o_id, o_parentId, o_type, o_key, o_path, o_classId, o_className, o_creationDate, o_modificationDate) VALUES
(1, 0, 'folder', 'customers', '/', NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 1, 'object', 'john-doe', '/customers/', 'CU', 'Customer', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 1, 'object', 'jane-smith', '/customers/', 'CU', 'Customer', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 1, 'object', 'bob-wilson', '/customers/', 'CU', 'Customer', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(5, 0, 'folder', 'segments', '/', NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(6, 5, 'object', 'premium-tier', '/segments/', 'CS', 'CustomerSegment', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(7, 5, 'object', 'newsletter-subscriber', '/segments/', 'CS', 'CustomerSegment', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(8, 5, 'object', 'enterprise-client', '/segments/', 'CS', 'CustomerSegment', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(9, 0, 'folder', 'products', '/', NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(10, 9, 'object', 'product-a', '/products/', 'PR', 'Product', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Documents
INSERT INTO documents (id, parentId, type, `key`, path, published, creationDate, modificationDate) VALUES
(1, 0, 'page', 'home', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 0, 'page', 'about', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 0, 'page', 'contact', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 1, 'page', 'landing', '/home/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Assets
INSERT INTO assets (id, parentId, type, filename, path, mimetype, creationDate, modificationDate) VALUES
(1, 0, 'folder', 'images', '/', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 1, 'image', 'logo.png', '/images/', 'image/png', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 1, 'image', 'banner.jpg', '/images/', 'image/jpeg', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Segment assignments
INSERT INTO plugin_cmf_segment_assignment (elementId, elementType, segmentId, breaksInheritance) VALUES
(2, 'object', 6, 0),
(2, 'object', 7, 0),
(3, 'object', 6, 0),
(3, 'object', 8, 1),
(4, 'object', 7, 0),
(4, 'document', 1, 0),
(2, 'document', 2, 0);

-- Customer segments
INSERT INTO plugin_cmf_customer_segments (name, `group`, reference, calculated, creationDate) VALUES
('Premium Tier', 'loyalty', 'premium-tier', 0, UNIX_TIMESTAMP()),
('Newsletter Subscriber', 'communication', 'newsletter-sub', 0, UNIX_TIMESTAMP()),
('Enterprise Client', 'business', 'enterprise', 0, UNIX_TIMESTAMP()),
('Trial User', 'onboarding', 'trial-user', 1, UNIX_TIMESTAMP());

-- Activities
INSERT INTO plugin_cmf_activities (customerId, activityDate, type, implementationClass, md5, creationDate) VALUES
(2, NOW(), 'login', 'CustomerManagementBundle\\Model\\Activity\\LoginActivity', MD5('login-2'), NOW()),
(3, NOW(), 'purchase', 'CustomerManagementBundle\\Model\\Activity\\PurchaseActivity', MD5('purchase-3'), NOW()),
(4, NOW(), 'pageview', 'CustomerManagementBundle\\Model\\Activity\\PageviewActivity', MD5('pageview-4'), NOW());

-- Action trigger rules
INSERT INTO plugin_cmf_action_trigger_rules (name, description, active, creationDate) VALUES
('Welcome Email', 'Send welcome email on first login', 1, UNIX_TIMESTAMP()),
('Upgrade Notification', 'Notify when eligible for upgrade', 1, UNIX_TIMESTAMP());

-- Admin user (default Pimcore admin)
INSERT INTO users (username, password, name, email, admin, active) VALUES
('admin', '$2y$10$jv6p3ZWgHAgk3OQlzuWz3eHle31P2TKBofmVNMlhWgoA1/IkMbbYe', 'Administrator', 'admin@pimcore-demo.local', 1, 1),
('editor', '$2y$10$jv6p3ZWgHAgk3OQlzuWz3eHle31P2TKBofmVNMlhWgoA1/IkMbbYe', 'Content Editor', 'editor@pimcore-demo.local', 0, 1);

-- System configuration with sensitive flag value
INSERT INTO system_configuration (config_key, config_value, scope, creationDate) VALUES
('general.timezone', 'UTC', 'system', UNIX_TIMESTAMP()),
('general.language', 'en', 'system', UNIX_TIMESTAMP()),
('email.sender.address', 'noreply@pimcore-demo.local', 'system', UNIX_TIMESTAMP()),
('email.smtp.host', 'smtp.pimcore-demo.local', 'system', UNIX_TIMESTAMP()),
('system.secret', '@FLAG@', 'system', UNIX_TIMESTAMP()),
('cache.lifetime', '3600', 'system', UNIX_TIMESTAMP()),
('assets.max_upload', '104857600', 'system', UNIX_TIMESTAMP());
