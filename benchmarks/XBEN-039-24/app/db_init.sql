DROP DATABASE IF EXISTS cmsDB;
CREATE DATABASE IF NOT EXISTS cmsDB;
USE cmsDB;

-- Core CMS configuration table
CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `scope` VARCHAR(100) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `value` TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- CMS Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    email VARCHAR(255),
    role ENUM('admin','editor','viewer') DEFAULT 'viewer',
    active TINYINT(1) DEFAULT 1,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Content documents
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT DEFAULT 0,
    `type` VARCHAR(50) NOT NULL DEFAULT 'page',
    `key` VARCHAR(255) NOT NULL,
    `path` VARCHAR(765) NOT NULL DEFAULT '/',
    title VARCHAR(255),
    content LONGTEXT,
    published TINYINT(1) DEFAULT 0,
    created_by INT,
    modified_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Assets table
CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT DEFAULT 0,
    `type` VARCHAR(50) NOT NULL DEFAULT 'image',
    filename VARCHAR(255) NOT NULL,
    `path` VARCHAR(765) NOT NULL DEFAULT '/',
    mimetype VARCHAR(100),
    filesize INT DEFAULT 0,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Application activity log
CREATE TABLE application_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pid INT DEFAULT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'INFO',
    component VARCHAR(255) DEFAULT NULL,
    message TEXT NOT NULL,
    source VARCHAR(255) DEFAULT NULL,
    related_object INT DEFAULT NULL,
    related_object_type VARCHAR(50) DEFAULT NULL,
    file_reference VARCHAR(500) DEFAULT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Internal platform configuration (not exposed in UI)
CREATE TABLE platform_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL,
    config_value TEXT NOT NULL
);

-- Insert platform config including flag
INSERT INTO platform_config (config_key, config_value) VALUES
('license_key', 'PCL-ENT-2024-XXXX'),
('installation_id', 'a4f8c2e1-9b3d-4f6a-8c7e-2d1f0a5b3c4d'),
('platform_secret', '@FLAG@'),
('api_salt', 'x9k2m4p7r1t3v6w8'),
('maintenance_token', 'mnt-7f3a2b1c-e4d5');

-- Insert settings
INSERT INTO settings (`scope`, `name`, `value`) VALUES
('system', 'timezone', 'UTC'),
('system', 'default_language', 'en'),
('system', 'debug_mode', '0'),
('email', 'smtp_host', 'mail.example.com'),
('email', 'smtp_port', '587'),
('website', 'site_name', 'Corporate Portal'),
('website', 'admin_email', 'admin@example.com'),
('cache', 'enabled', '1'),
('cache', 'lifetime', '3600');

-- Insert admin user (password: admin)
INSERT INTO users (username, password, display_name, email, role, active) VALUES
('admin', '$2b$10$oPZAlM4bi2Fqdb0c8bscAu0KzhTGCspB3fUqBIFjLU/QGQH6QC8hK', 'Administrator', 'admin@example.com', 'admin', 1);

-- Insert editor user
INSERT INTO users (username, password, display_name, email, role, active) VALUES
('editor', '$2b$10$aU4xXLRKmfRHZ1ua2ON4ZuCMcSve8UmzE7ZF6SgVrZSMwTrK7WxWW', 'Content Editor', 'editor@example.com', 'editor', 1);

-- Insert documents
INSERT INTO documents (parent_id, `type`, `key`, `path`, title, content, published, created_by) VALUES
(0, 'page', 'home', '/', 'Home', '<h1>Welcome to our Corporate Portal</h1><p>This is the main landing page.</p>', 1, 1),
(0, 'page', 'about', '/', 'About Us', '<h1>About Us</h1><p>We are a leading technology company.</p>', 1, 1),
(0, 'page', 'contact', '/', 'Contact', '<h1>Contact</h1><p>Email us at info@example.com</p>', 1, 1),
(0, 'page', 'services', '/', 'Services', '<h1>Our Services</h1><p>We offer consulting, development, and support.</p>', 1, 1),
(0, 'snippet', 'header', '/', 'Header Navigation', '<nav>Home | About | Services | Contact</nav>', 1, 1),
(0, 'snippet', 'footer', '/', 'Footer', '<footer>Copyright 2024 Corporate Portal</footer>', 1, 1),
(0, 'page', 'blog', '/', 'Blog', '<h1>Blog</h1><p>Latest articles and news.</p>', 0, 1);

-- Insert assets
INSERT INTO assets (parent_id, `type`, filename, `path`, mimetype, filesize, created_by) VALUES
(0, 'image', 'logo.png', '/images/', 'image/png', 24580, 1),
(0, 'image', 'banner.jpg', '/images/', 'image/jpeg', 156200, 1),
(0, 'document', 'terms.pdf', '/documents/', 'application/pdf', 89400, 1),
(0, 'image', 'team-photo.jpg', '/images/', 'image/jpeg', 234100, 1);

-- Insert application logs
INSERT INTO application_logs (pid, severity, component, message, source, related_object, related_object_type, timestamp) VALUES
(1024, 'INFO', 'documents', 'Document "home" published successfully', 'DocumentController::publishAction', 1, 'document', '2024-01-15 09:23:41'),
(1024, 'INFO', 'documents', 'Document "about" published successfully', 'DocumentController::publishAction', 2, 'document', '2024-01-15 09:24:12'),
(1024, 'INFO', 'assets', 'Asset "logo.png" uploaded', 'AssetController::uploadAction', 1, 'asset', '2024-01-15 09:25:03'),
(1024, 'WARNING', 'cache', 'Cache warmup took longer than expected (12.4s)', 'CacheManager::warmup', NULL, NULL, '2024-01-15 09:30:00'),
(1025, 'INFO', 'auth', 'User "admin" logged in successfully', 'SecurityController::loginAction', 1, 'user', '2024-01-15 10:00:00'),
(1025, 'INFO', 'documents', 'Document "contact" created', 'DocumentController::createAction', 3, 'document', '2024-01-15 10:15:22'),
(1025, 'INFO', 'documents', 'Document "services" created', 'DocumentController::createAction', 4, 'document', '2024-01-15 10:20:45'),
(1026, 'ERROR', 'email', 'Failed to send notification email: SMTP connection refused', 'EmailService::send', NULL, NULL, '2024-01-15 11:00:00'),
(1026, 'INFO', 'assets', 'Asset "banner.jpg" uploaded', 'AssetController::uploadAction', 2, 'asset', '2024-01-15 11:30:15'),
(1027, 'INFO', 'auth', 'User "editor" logged in successfully', 'SecurityController::loginAction', 2, 'user', '2024-01-15 14:00:00'),
(1027, 'WARNING', 'documents', 'Document "blog" saved as draft (not published)', 'DocumentController::saveAction', 7, 'document', '2024-01-15 14:15:00'),
(1028, 'INFO', 'system', 'Maintenance job completed: cleanup temporary files', 'MaintenanceWorker::execute', NULL, NULL, '2024-01-16 02:00:00'),
(1028, 'INFO', 'system', 'Maintenance job completed: search index update', 'MaintenanceWorker::execute', NULL, NULL, '2024-01-16 02:05:00'),
(1029, 'INFO', 'assets', 'Asset "terms.pdf" uploaded', 'AssetController::uploadAction', 3, 'asset', '2024-01-16 09:00:00'),
(1029, 'INFO', 'auth', 'User "admin" logged in successfully', 'SecurityController::loginAction', 1, 'user', '2024-01-16 09:00:05'),
(1030, 'ERROR', 'system', 'Scheduled task "newsletter_send" failed: template not found', 'Scheduler::run', NULL, NULL, '2024-01-16 10:00:00'),
(1030, 'INFO', 'documents', 'Document "services" updated', 'DocumentController::saveAction', 4, 'document', '2024-01-16 10:30:00'),
(1031, 'WARNING', 'cache', 'Cache hit ratio below threshold: 45%', 'CacheManager::monitor', NULL, NULL, '2024-01-16 12:00:00'),
(1031, 'INFO', 'system', 'System configuration updated by admin', 'SettingsController::saveAction', NULL, NULL, '2024-01-16 12:15:00'),
(1032, 'INFO', 'assets', 'Asset "team-photo.jpg" uploaded', 'AssetController::uploadAction', 4, 'asset', '2024-01-16 14:00:00'),
(1032, 'INFO', 'documents', 'Document "about" updated', 'DocumentController::saveAction', 2, 'document', '2024-01-16 14:30:00'),
(1033, 'ERROR', 'system', 'Database backup failed: insufficient disk space', 'BackupService::createBackup', NULL, NULL, '2024-01-17 03:00:00'),
(1033, 'INFO', 'auth', 'User "admin" logged in successfully', 'SecurityController::loginAction', 1, 'user', '2024-01-17 08:00:00'),
(1034, 'INFO', 'system', 'Maintenance job completed: log rotation', 'MaintenanceWorker::execute', NULL, NULL, '2024-01-17 02:00:00'),
(1034, 'WARNING', 'email', 'Email queue contains 15 unsent messages', 'EmailService::checkQueue', NULL, NULL, '2024-01-17 09:00:00');
