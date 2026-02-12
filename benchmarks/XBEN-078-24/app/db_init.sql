CREATE DATABASE IF NOT EXISTS pimcore;
USE pimcore;

-- Clean up existing tables if present
DROP TABLE IF EXISTS settings_store;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS translations_admin;
DROP TABLE IF EXISTS translations_messages;
DROP TABLE IF EXISTS users;

-- Users table for admin authentication
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(190) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    admin TINYINT(1) DEFAULT 0,
    active TINYINT(1) DEFAULT 1,
    language VARCHAR(10) DEFAULT 'en',
    lastLogin DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Translations messages table (website translations)
CREATE TABLE translations_messages (
    `key` VARCHAR(190) NOT NULL DEFAULT '',
    `type` VARCHAR(10) DEFAULT NULL,
    `language` VARCHAR(10) NOT NULL DEFAULT '',
    `text` TEXT DEFAULT NULL,
    `creationDate` INT UNSIGNED DEFAULT NULL,
    `modificationDate` INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (`key`, `language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Translations admin table (admin interface translations)
CREATE TABLE translations_admin (
    `key` VARCHAR(190) NOT NULL DEFAULT '',
    `type` VARCHAR(10) DEFAULT NULL,
    `language` VARCHAR(10) NOT NULL DEFAULT '',
    `text` TEXT DEFAULT NULL,
    `creationDate` INT UNSIGNED DEFAULT NULL,
    `modificationDate` INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (`key`, `language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Assets table
CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    `type` VARCHAR(20) DEFAULT NULL,
    filename VARCHAR(255) DEFAULT NULL,
    path VARCHAR(765) DEFAULT NULL,
    mimetype VARCHAR(190) DEFAULT NULL,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    userOwner INT UNSIGNED DEFAULT NULL,
    userModification INT UNSIGNED DEFAULT NULL
);

-- Documents table
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    `type` VARCHAR(20) DEFAULT NULL,
    `key` VARCHAR(255) DEFAULT '',
    path VARCHAR(765) DEFAULT NULL,
    published TINYINT(1) DEFAULT 1,
    creationDate INT UNSIGNED DEFAULT NULL,
    modificationDate INT UNSIGNED DEFAULT NULL,
    userOwner INT UNSIGNED DEFAULT NULL,
    userModification INT UNSIGNED DEFAULT NULL
);

-- System settings / configuration
CREATE TABLE settings_store (
    id VARCHAR(190) NOT NULL DEFAULT '',
    scope VARCHAR(190) NOT NULL DEFAULT '',
    data TEXT DEFAULT NULL,
    `type` VARCHAR(20) DEFAULT NULL,
    PRIMARY KEY (id, scope)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert admin user (password: admin)
INSERT INTO users (username, password, name, email, admin, active, language) VALUES
('admin', '$2y$10$WXe0amotmEmXQ3lO0MpDXOomIiOP05HstSlKovRh2rB10RaxxMDeW', 'Admin User', 'admin@pimcore.local', 1, 1, 'en');

-- Insert sample website translations
INSERT INTO translations_messages (`key`, `type`, `language`, `text`, `creationDate`, `modificationDate`) VALUES
('general.welcome', 'simple', 'en', 'Welcome to our website', 1680000000, 1680000000),
('general.welcome', 'simple', 'de', 'Willkommen auf unserer Webseite', 1680000000, 1680000000),
('general.welcome', 'simple', 'fr', 'Bienvenue sur notre site', 1680000000, 1680000000),
('nav.home', 'simple', 'en', 'Home', 1680000000, 1680000000),
('nav.home', 'simple', 'de', 'Startseite', 1680000000, 1680000000),
('nav.home', 'simple', 'fr', 'Accueil', 1680000000, 1680000000),
('nav.about', 'simple', 'en', 'About Us', 1680000000, 1680000000),
('nav.about', 'simple', 'de', 'Über Uns', 1680000000, 1680000000),
('nav.about', 'simple', 'fr', 'À Propos', 1680000000, 1680000000),
('nav.contact', 'simple', 'en', 'Contact', 1680000000, 1680000000),
('nav.contact', 'simple', 'de', 'Kontakt', 1680000000, 1680000000),
('nav.contact', 'simple', 'fr', 'Contact', 1680000000, 1680000000),
('footer.copyright', 'simple', 'en', '© 2023 All rights reserved', 1680000000, 1680000000),
('footer.copyright', 'simple', 'de', '© 2023 Alle Rechte vorbehalten', 1680000000, 1680000000),
('footer.copyright', 'simple', 'fr', '© 2023 Tous droits réservés', 1680000000, 1680000000),
('btn.submit', 'simple', 'en', 'Submit', 1680000000, 1680000000),
('btn.submit', 'simple', 'de', 'Absenden', 1680000000, 1680000000),
('btn.submit', 'simple', 'fr', 'Soumettre', 1680000000, 1680000000),
('btn.cancel', 'simple', 'en', 'Cancel', 1680000000, 1680000000),
('btn.cancel', 'simple', 'de', 'Abbrechen', 1680000000, 1680000000),
('btn.cancel', 'simple', 'fr', 'Annuler', 1680000000, 1680000000),
('error.notfound', 'simple', 'en', 'Page not found', 1680000000, 1680000000),
('error.notfound', 'simple', 'de', 'Seite nicht gefunden', 1680000000, 1680000000),
('error.notfound', 'simple', 'fr', 'Page non trouvée', 1680000000, 1680000000),
('msg.success', 'simple', 'en', 'Operation completed successfully', 1680000000, 1680000000),
('msg.success', 'simple', 'de', 'Vorgang erfolgreich abgeschlossen', 1680000000, 1680000000),
('msg.success', 'simple', 'fr', 'Opération terminée avec succès', 1680000000, 1680000000);

-- Insert sample admin translations
INSERT INTO translations_admin (`key`, `type`, `language`, `text`, `creationDate`, `modificationDate`) VALUES
('admin.dashboard', 'simple', 'en', 'Dashboard', 1680000000, 1680000000),
('admin.dashboard', 'simple', 'de', 'Übersicht', 1680000000, 1680000000),
('admin.assets', 'simple', 'en', 'Assets', 1680000000, 1680000000),
('admin.assets', 'simple', 'de', 'Medien', 1680000000, 1680000000),
('admin.documents', 'simple', 'en', 'Documents', 1680000000, 1680000000),
('admin.documents', 'simple', 'de', 'Dokumente', 1680000000, 1680000000),
('admin.settings', 'simple', 'en', 'Settings', 1680000000, 1680000000),
('admin.settings', 'simple', 'de', 'Einstellungen', 1680000000, 1680000000),
('admin.users', 'simple', 'en', 'Users', 1680000000, 1680000000),
('admin.users', 'simple', 'de', 'Benutzer', 1680000000, 1680000000);

-- Insert sample assets
INSERT INTO assets (parentId, `type`, filename, path, mimetype, creationDate, modificationDate, userOwner) VALUES
(0, 'folder', 'images', '/', NULL, 1680000000, 1680000000, 1),
(1, 'image', 'logo.png', '/images/', 'image/png', 1680000000, 1680000000, 1),
(1, 'image', 'banner.jpg', '/images/', 'image/jpeg', 1680000000, 1680000000, 1),
(0, 'folder', 'documents', '/', NULL, 1680000000, 1680000000, 1);

-- Insert sample documents
INSERT INTO documents (parentId, `type`, `key`, path, published, creationDate, modificationDate, userOwner) VALUES
(0, 'page', '', '/', 1, 1680000000, 1680000000, 1),
(1, 'page', 'about', '/', 1, 1680000000, 1680000000, 1),
(1, 'page', 'contact', '/', 1, 1680000000, 1680000000, 1),
(1, 'page', 'blog', '/', 1, 1680000000, 1680000000, 1);

-- System settings - including flag stored as an internal configuration value
INSERT INTO settings_store (id, scope, data, `type`) VALUES
('system.hostname', 'pimcore', 'pimcore.local', 'string'),
('system.timezone', 'pimcore', 'UTC', 'string'),
('system.languages.default', 'pimcore', 'en', 'string'),
('system.languages.available', 'pimcore', 'en,de,fr', 'string'),
('system.debug', 'pimcore', '0', 'bool'),
('system.email.sender', 'pimcore', 'noreply@pimcore.local', 'string'),
('system.email.method', 'pimcore', 'smtp', 'string'),
('system.cache.enabled', 'pimcore', '1', 'bool'),
('system.maintenance.secret', 'pimcore', '@FLAG@', 'string'),
('system.version', 'pimcore', '10.5.20', 'string'),
('system.installationId', 'pimcore', 'a4b2c8d1-e5f6-4a3b-9c7d-2e1f0a8b6c4d', 'string');
