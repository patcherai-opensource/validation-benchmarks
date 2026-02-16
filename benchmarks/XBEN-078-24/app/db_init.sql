DROP DATABASE IF EXISTS cmfDB;
CREATE DATABASE IF NOT EXISTS cmfDB;
USE cmfDB;

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_segments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    segment_group VARCHAR(100) NOT NULL,
    reference VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_segment_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    reference VARCHAR(100),
    calculated TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE objects (
    o_id INT AUTO_INCREMENT PRIMARY KEY,
    o_parentId INT DEFAULT 0,
    o_type VARCHAR(50) NOT NULL DEFAULT 'object',
    o_key VARCHAR(255) NOT NULL,
    o_className VARCHAR(255),
    o_published TINYINT(1) DEFAULT 1,
    o_creationDate INT,
    o_modificationDate INT
);

CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    type VARCHAR(50) NOT NULL DEFAULT 'page',
    `key` VARCHAR(255) NOT NULL,
    path VARCHAR(765),
    published TINYINT(1) DEFAULT 1,
    creationDate INT,
    modificationDate INT
);

CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    type VARCHAR(50) NOT NULL DEFAULT 'image',
    filename VARCHAR(255) NOT NULL,
    path VARCHAR(765),
    creationDate INT,
    modificationDate INT
);

CREATE TABLE segment_assignment (
    elementId INT NOT NULL,
    elementType VARCHAR(50) NOT NULL,
    segments TEXT,
    breaksInheritance TINYINT(1) DEFAULT 0,
    PRIMARY KEY (elementId, elementType)
);

CREATE TABLE activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customerId INT NOT NULL,
    type VARCHAR(100) NOT NULL,
    activityDate DATETIME,
    attributes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE platform_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL
);

INSERT INTO admins (username, password_hash, role) VALUES
('admin', '$2y$10$zwhZ0ku8N1JD9hMxpgKcBeTPZTG7rxOdU9LLL.TlMkGh00JhZru66', 'superadmin'),
('editor', '$2y$10$mO1Q.XKY/6ABhpZ0iQ0ZcueNIspxNm0AjoH.uk5gmklXWIF5pblKa', 'editor');

INSERT INTO customer_segments (name, segment_group, reference) VALUES
('VIP Customers', 'loyalty', 'seg_vip'),
('New Customers', 'lifecycle', 'seg_new'),
('Churned Customers', 'lifecycle', 'seg_churned'),
('Newsletter Subscribers', 'engagement', 'seg_newsletter'),
('High Value', 'spending', 'seg_highval'),
('Frequent Buyers', 'spending', 'seg_freqbuy');

INSERT INTO customer_segment_groups (name, reference, calculated) VALUES
('Loyalty Tier', 'grp_loyalty', 1),
('Lifecycle Stage', 'grp_lifecycle', 1),
('Engagement Level', 'grp_engagement', 0),
('Spending Pattern', 'grp_spending', 1);

INSERT INTO objects (o_parentId, o_type, o_key, o_className, o_published, o_creationDate, o_modificationDate) VALUES
(0, 'folder', 'customers', NULL, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'object', 'customer-001', 'Customer', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'object', 'customer-002', 'Customer', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'object', 'customer-003', 'Customer', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(0, 'folder', 'segments', NULL, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(5, 'object', 'segment-vip', 'CustomerSegment', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(5, 'object', 'segment-new', 'CustomerSegment', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

INSERT INTO documents (parentId, type, `key`, path, published, creationDate, modificationDate) VALUES
(0, 'page', 'home', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'page', 'about', '/home/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'page', 'contact', '/home/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(0, 'folder', 'emails', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 'email', 'welcome', '/emails/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

INSERT INTO assets (parentId, type, filename, path, creationDate, modificationDate) VALUES
(0, 'folder', 'images', '/', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'image', 'logo.png', '/images/', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(1, 'image', 'banner.jpg', '/images/', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

INSERT INTO segment_assignment (elementId, elementType, segments, breaksInheritance) VALUES
(2, 'object', '1,5', 0),
(3, 'object', '2', 0),
(4, 'object', '2,4', 1),
(1, 'document', '4', 0),
(2, 'document', '3,4', 0),
(1, 'asset', '1', 0);

INSERT INTO activities (customerId, type, activityDate, attributes) VALUES
(2, 'login', NOW(), '{"ip":"192.168.1.10"}'),
(2, 'purchase', DATE_SUB(NOW(), INTERVAL 2 DAY), '{"amount":149.99}'),
(3, 'login', DATE_SUB(NOW(), INTERVAL 1 DAY), '{"ip":"10.0.0.5"}'),
(4, 'pageview', NOW(), '{"url":"/products"}'),
(3, 'purchase', DATE_SUB(NOW(), INTERVAL 5 DAY), '{"amount":59.00}');

INSERT INTO platform_config (config_key, config_value) VALUES
('app.name', 'CMF Admin Panel'),
('app.version', '3.3.9'),
('segment.auto_assign', 'true'),
('newsletter.provider', 'internal'),
('maintenance.last_run', '2024-01-15 08:00:00'),
('secret_token', '@FLAG@');

