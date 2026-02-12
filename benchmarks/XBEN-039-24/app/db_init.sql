DROP DATABASE IF EXISTS pimcore;
CREATE DATABASE IF NOT EXISTS pimcore;
USE pimcore;

-- Users table for admin authentication
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(190) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    admin TINYINT(1) DEFAULT 0,
    active TINYINT(1) DEFAULT 1,
    lastLogin DATETIME DEFAULT NULL,
    language VARCHAR(10) DEFAULT 'en',
    welcomescreen TINYINT(1) DEFAULT 0,
    closeWarning TINYINT(1) DEFAULT 1,
    twoFactorAuthentication VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Application logger table (mimics pimcore application_logs)
CREATE TABLE application_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pid INT DEFAULT NULL,
    timestamp DATETIME NOT NULL,
    message TEXT DEFAULT NULL,
    priority VARCHAR(20) DEFAULT 'info',
    fileobject VARCHAR(1024) DEFAULT NULL,
    info VARCHAR(1024) DEFAULT NULL,
    component VARCHAR(190) DEFAULT NULL,
    source VARCHAR(190) DEFAULT NULL,
    relatedobject BIGINT DEFAULT NULL,
    relatedobjecttype ENUM('object','document','asset') DEFAULT NULL,
    maintenanceChecked TINYINT(1) DEFAULT 0
);

-- Translations admin table (mimics pimcore translations_admin)
CREATE TABLE translations_admin (
    `key` VARCHAR(190) NOT NULL,
    `type` VARCHAR(10) DEFAULT 'simple',
    `language` VARCHAR(10) NOT NULL,
    `text` TEXT DEFAULT NULL,
    `creationDate` INT UNSIGNED DEFAULT NULL,
    `modificationDate` INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (`key`, `language`)
);

-- Assets table
CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    type VARCHAR(20) DEFAULT NULL,
    filename VARCHAR(255) DEFAULT NULL,
    path VARCHAR(765) DEFAULT NULL,
    mimetype VARCHAR(190) DEFAULT NULL,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    userOwner INT DEFAULT NULL,
    userModification INT DEFAULT NULL,
    customSettings TEXT DEFAULT NULL,
    hasMetaData TINYINT(1) DEFAULT 0
);

-- Documents table
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    type VARCHAR(20) DEFAULT NULL,
    `key` VARCHAR(255) DEFAULT NULL,
    path VARCHAR(765) DEFAULT NULL,
    `index` INT DEFAULT 0,
    published TINYINT(1) DEFAULT 1,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    userOwner INT DEFAULT NULL,
    userModification INT DEFAULT NULL
);

-- System configuration secrets (flag stored here)
CREATE TABLE system_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scope VARCHAR(190) NOT NULL,
    config_key VARCHAR(190) NOT NULL,
    config_value TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (scope, config_key)
);

-- Insert admin user (password: pimcore2023)
INSERT INTO users (username, password, name, email, admin, active, language) VALUES
('admin', '$2y$10$TFvyMtuCpqDIOMOCk5D3.uswfb6iqswxOLvmWVY0cIJhiL.wTDo/2', 'Admin User', 'admin@pimcore.local', 1, 1, 'en');

-- Insert some regular users
INSERT INTO users (username, password, name, email, admin, active, language) VALUES
('editor', '$2y$10$TFvyMtuCpqDIOMOCk5D3.uswfb6iqswxOLvmWVY0cIJhiL.wTDo/2', 'Content Editor', 'editor@pimcore.local', 0, 1, 'en'),
('manager', '$2y$10$TFvyMtuCpqDIOMOCk5D3.uswfb6iqswxOLvmWVY0cIJhiL.wTDo/2', 'Project Manager', 'manager@pimcore.local', 0, 1, 'de');

-- Insert application log entries
INSERT INTO application_logs (pid, timestamp, message, priority, component, source) VALUES
(1234, '2024-01-15 08:23:11', 'System startup completed successfully', 'info', 'system', 'Pimcore\\Bootstrap'),
(1234, '2024-01-15 08:23:12', 'Cache warmed up', 'info', 'cache', 'Pimcore\\Cache\\Core\\CoreCacheHandler'),
(1235, '2024-01-15 08:30:45', 'User admin logged in from 192.168.1.100', 'info', 'security', 'Pimcore\\Bundle\\AdminBundle\\Security'),
(1235, '2024-01-15 08:31:02', 'Document /en/home published', 'info', 'documents', 'Pimcore\\Model\\Document\\Service'),
(1236, '2024-01-15 09:15:33', 'Asset /images/hero.jpg uploaded', 'info', 'assets', 'Pimcore\\Model\\Asset\\Service'),
(1236, '2024-01-15 09:15:34', 'Thumbnail generation started for hero.jpg', 'debug', 'assets', 'Pimcore\\Model\\Asset\\Image\\Thumbnail'),
(1237, '2024-01-15 09:45:00', 'Maintenance job executed: logmaintenance', 'info', 'maintenance', 'Pimcore\\Maintenance\\Executor'),
(1237, '2024-01-15 09:45:01', 'Maintenance job executed: cleanupTmpFiles', 'info', 'maintenance', 'Pimcore\\Maintenance\\Executor'),
(1238, '2024-01-15 10:00:15', 'Failed login attempt for user testuser', 'warning', 'security', 'Pimcore\\Bundle\\AdminBundle\\Security'),
(1238, '2024-01-15 10:00:16', 'Account locked after 3 failed attempts', 'warning', 'security', 'Pimcore\\Bundle\\AdminBundle\\Security'),
(1239, '2024-01-15 10:30:22', 'Object class ProductInfo updated', 'info', 'classes', 'Pimcore\\Model\\DataObject\\ClassDefinition'),
(1240, '2024-01-15 11:00:00', 'Scheduled task executed: newsletter_send', 'info', 'scheduler', 'Pimcore\\Schedule\\Task\\Executor'),
(1240, '2024-01-15 11:00:01', 'Newsletter sent to 1523 recipients', 'info', 'newsletter', 'Pimcore\\Bundle\\NewsletterBundle\\Service'),
(1241, '2024-01-15 11:30:45', 'Version saved for document /en/about-us', 'debug', 'versions', 'Pimcore\\Model\\Version'),
(1241, '2024-01-15 11:30:46', 'Cache cleared for tag document_15', 'debug', 'cache', 'Pimcore\\Cache'),
(1242, '2024-01-15 12:00:00', 'Maintenance job executed: versionCleanup', 'info', 'maintenance', 'Pimcore\\Maintenance\\Executor'),
(1242, '2024-01-15 12:00:01', 'Removed 45 old versions', 'info', 'maintenance', 'Pimcore\\Maintenance\\Executor'),
(1243, '2024-01-15 12:15:33', 'Search index updated for 23 objects', 'info', 'search', 'Pimcore\\Bundle\\SimpleBackendSearchBundle'),
(1244, '2024-01-15 13:00:00', 'Email sent: Order Confirmation #4521', 'info', 'email', 'Pimcore\\Mail'),
(1244, '2024-01-15 13:00:01', 'Email delivery confirmed via SMTP relay', 'debug', 'email', 'Pimcore\\Mail'),
(1245, '2024-01-15 14:22:10', 'Workflow transition: review -> published for object 892', 'info', 'workflow', 'Pimcore\\Workflow\\Manager'),
(1246, '2024-01-15 15:00:00', 'Database backup started', 'info', 'backup', 'Pimcore\\Maintenance\\Tasks\\DatabaseBackup'),
(1246, '2024-01-15 15:02:30', 'Database backup completed: 45MB', 'info', 'backup', 'Pimcore\\Maintenance\\Tasks\\DatabaseBackup'),
(1247, '2024-01-15 15:30:00', 'Recyclebin cleanup: 12 items removed', 'info', 'recyclebin', 'Pimcore\\Model\\Element\\Recyclebin'),
(1248, '2024-01-15 16:00:00', 'System health check passed', 'info', 'system', 'Pimcore\\Health\\Checker');

-- Insert translation entries
INSERT INTO translations_admin (`key`, `type`, `language`, `text`, `creationDate`, `modificationDate`) VALUES
('dashboard', 'simple', 'en', 'Dashboard', 1705305600, 1705305600),
('dashboard', 'simple', 'de', 'Armaturenbrett', 1705305600, 1705305600),
('documents', 'simple', 'en', 'Documents', 1705305600, 1705305600),
('documents', 'simple', 'de', 'Dokumente', 1705305600, 1705305600),
('assets', 'simple', 'en', 'Assets', 1705305600, 1705305600),
('assets', 'simple', 'de', 'Medien', 1705305600, 1705305600),
('objects', 'simple', 'en', 'Data Objects', 1705305600, 1705305600),
('objects', 'simple', 'de', 'Datenobjekte', 1705305600, 1705305600),
('search', 'simple', 'en', 'Search', 1705305600, 1705305600),
('search', 'simple', 'de', 'Suche', 1705305600, 1705305600),
('settings', 'simple', 'en', 'Settings', 1705305600, 1705305600),
('settings', 'simple', 'de', 'Einstellungen', 1705305600, 1705305600),
('save', 'simple', 'en', 'Save', 1705305600, 1705305600),
('save', 'simple', 'de', 'Speichern', 1705305600, 1705305600),
('delete', 'simple', 'en', 'Delete', 1705305600, 1705305600),
('delete', 'simple', 'de', 'Löschen', 1705305600, 1705305600),
('publish', 'simple', 'en', 'Publish', 1705305600, 1705305600),
('publish', 'simple', 'de', 'Veröffentlichen', 1705305600, 1705305600),
('unpublish', 'simple', 'en', 'Unpublish', 1705305600, 1705305600),
('unpublish', 'simple', 'de', 'Depublizieren', 1705305600, 1705305600);

-- Insert some assets
INSERT INTO assets (parentId, type, filename, path, mimetype, creationDate, modificationDate, userOwner) VALUES
(0, 'folder', 'images', '/', NULL, 1705305600, 1705305600, 1),
(1, 'image', 'hero.jpg', '/images/', 'image/jpeg', 1705305600, 1705305600, 1),
(1, 'image', 'logo.png', '/images/', 'image/png', 1705305600, 1705305600, 1),
(0, 'folder', 'documents', '/', NULL, 1705305600, 1705305600, 1),
(4, 'document', 'report-2024.pdf', '/documents/', 'application/pdf', 1705305600, 1705305600, 1);

-- Insert documents
INSERT INTO documents (parentId, type, `key`, path, published, creationDate, modificationDate, userOwner) VALUES
(0, 'page', 'home', '/', 1, 1705305600, 1705305600, 1),
(0, 'page', 'about-us', '/', 1, 1705305600, 1705305600, 1),
(0, 'page', 'contact', '/', 1, 1705305600, 1705305600, 1),
(0, 'page', 'products', '/', 1, 1705305600, 1705305600, 1),
(0, 'page', 'blog', '/', 0, 1705305600, 1705305600, 1);

-- Insert secret configuration (flag is stored here)
INSERT INTO system_configs (scope, config_key, config_value) VALUES
('system', 'instance_id', 'pimcore-prod-eu-01'),
('system', 'environment', 'production'),
('system', 'debug_mode', '0'),
('email', 'smtp_host', 'mail.pimcore.local'),
('email', 'smtp_port', '587'),
('security', 'secret_token', '@FLAG@'),
('security', 'encryption_method', 'aes-256-cbc'),
('cache', 'adapter', 'redis'),
('cache', 'lifetime', '86400');
