DROP DATABASE IF EXISTS cmsDB;
CREATE DATABASE IF NOT EXISTS cmsDB;
USE cmsDB;

-- Core content translations table (mirrors Pimcore's translations_messages)
CREATE TABLE translations_messages (
    `key` VARCHAR(190) NOT NULL DEFAULT '',
    `type` VARCHAR(10) DEFAULT NULL,
    `language` VARCHAR(10) NOT NULL DEFAULT '',
    `text` TEXT DEFAULT NULL,
    `creationDate` INT(11) UNSIGNED DEFAULT NULL,
    `modificationDate` INT(11) UNSIGNED DEFAULT NULL,
    PRIMARY KEY (`key`, `language`),
    KEY `language` (`language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Admin translations table
CREATE TABLE translations_admin (
    `key` VARCHAR(190) NOT NULL DEFAULT '',
    `type` VARCHAR(10) DEFAULT NULL,
    `language` VARCHAR(10) NOT NULL DEFAULT '',
    `text` TEXT DEFAULT NULL,
    `creationDate` INT(11) UNSIGNED DEFAULT NULL,
    `modificationDate` INT(11) UNSIGNED DEFAULT NULL,
    PRIMARY KEY (`key`, `language`),
    KEY `language` (`language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Users table for admin authentication
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(100) DEFAULT NULL,
    lastname VARCHAR(100) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    admin TINYINT(1) DEFAULT 0,
    active TINYINT(1) DEFAULT 1,
    language VARCHAR(10) DEFAULT 'en',
    lastLogin INT(11) UNSIGNED DEFAULT NULL,
    creationDate INT(11) UNSIGNED DEFAULT NULL,
    modificationDate INT(11) UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Documents table for content pages
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    `type` VARCHAR(20) DEFAULT 'page',
    `key` VARCHAR(255) NOT NULL DEFAULT '',
    `path` VARCHAR(765) DEFAULT '/',
    published TINYINT(1) DEFAULT 1,
    creationDate INT(11) UNSIGNED DEFAULT NULL,
    modificationDate INT(11) UNSIGNED DEFAULT NULL,
    userOwner INT DEFAULT NULL,
    userModification INT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Assets metadata
CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parentId INT DEFAULT 0,
    `type` VARCHAR(20) DEFAULT 'image',
    filename VARCHAR(255) NOT NULL DEFAULT '',
    `path` VARCHAR(765) DEFAULT '/',
    mimetype VARCHAR(100) DEFAULT NULL,
    creationDate INT(11) UNSIGNED DEFAULT NULL,
    modificationDate INT(11) UNSIGNED DEFAULT NULL,
    userOwner INT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- System configuration (internal settings)
CREATE TABLE system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `scope` VARCHAR(100) NOT NULL,
    `key` VARCHAR(190) NOT NULL,
    `value` TEXT DEFAULT NULL,
    UNIQUE KEY `scope_key` (`scope`, `key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert admin user
INSERT INTO users (username, password, firstname, lastname, email, admin, active, language, creationDate, modificationDate)
VALUES ('admin', '$2y$10$5kBruRnlw1fsc6/utYPrCOIYIyJkAP6F99Tg/Zg6Fak9qW7.L3uJ.', 'System', 'Administrator', 'admin@example.com', 1, 1, 'en', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert editor user
INSERT INTO users (username, password, firstname, lastname, email, admin, active, language, creationDate, modificationDate)
VALUES ('editor', '$2y$10$MHlMu10RLt.BtsLzyRjhyuwmlIqiD526pRmjDPFvwk5s7Jxr562kS', 'Content', 'Editor', 'editor@example.com', 0, 1, 'en', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert sample website translations
INSERT INTO translations_messages (`key`, `type`, `language`, `text`, `creationDate`, `modificationDate`) VALUES
('homepage.title', 'simple', 'en', 'Welcome to our Website', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('homepage.title', 'simple', 'de', 'Willkommen auf unserer Webseite', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('homepage.title', 'simple', 'fr', 'Bienvenue sur notre site Web', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('homepage.description', 'simple', 'en', 'Your content management platform', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('homepage.description', 'simple', 'de', 'Ihre Content-Management-Plattform', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('homepage.description', 'simple', 'fr', 'Votre plateforme de gestion de contenu', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.home', 'simple', 'en', 'Home', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.home', 'simple', 'de', 'Startseite', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.home', 'simple', 'fr', 'Accueil', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.about', 'simple', 'en', 'About Us', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.about', 'simple', 'de', 'Über uns', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.about', 'simple', 'fr', 'À propos', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.contact', 'simple', 'en', 'Contact', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.contact', 'simple', 'de', 'Kontakt', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('nav.contact', 'simple', 'fr', 'Contact', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('footer.copyright', 'simple', 'en', '© 2024 All rights reserved', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('footer.copyright', 'simple', 'de', '© 2024 Alle Rechte vorbehalten', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('footer.copyright', 'simple', 'fr', '© 2024 Tous droits réservés', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('btn.submit', 'simple', 'en', 'Submit', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('btn.submit', 'simple', 'de', 'Absenden', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('btn.submit', 'simple', 'fr', 'Soumettre', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('btn.cancel', 'simple', 'en', 'Cancel', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('btn.cancel', 'simple', 'de', 'Abbrechen', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('btn.cancel', 'simple', 'fr', 'Annuler', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('error.notfound', 'simple', 'en', 'Page not found', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('error.notfound', 'simple', 'de', 'Seite nicht gefunden', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('error.notfound', 'simple', 'fr', 'Page non trouvée', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('form.name', 'simple', 'en', 'Your Name', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('form.name', 'simple', 'de', 'Ihr Name', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('form.name', 'simple', 'fr', 'Votre nom', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('form.email', 'simple', 'en', 'Email Address', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('form.email', 'simple', 'de', 'E-Mail-Adresse', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('form.email', 'simple', 'fr', 'Adresse e-mail', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('msg.success', 'simple', 'en', 'Operation completed successfully', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('msg.success', 'simple', 'de', 'Vorgang erfolgreich abgeschlossen', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('msg.success', 'simple', 'fr', 'Opération terminée avec succès', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert admin translations
INSERT INTO translations_admin (`key`, `type`, `language`, `text`, `creationDate`, `modificationDate`) VALUES
('admin.dashboard', 'simple', 'en', 'Dashboard', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.dashboard', 'simple', 'de', 'Übersicht', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.settings', 'simple', 'en', 'Settings', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.settings', 'simple', 'de', 'Einstellungen', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.users', 'simple', 'en', 'Users', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.users', 'simple', 'de', 'Benutzer', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.translations', 'simple', 'en', 'Translations', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.translations', 'simple', 'de', 'Übersetzungen', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.documents', 'simple', 'en', 'Documents', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.documents', 'simple', 'de', 'Dokumente', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.assets', 'simple', 'en', 'Assets', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.assets', 'simple', 'de', 'Medien', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.logout', 'simple', 'en', 'Logout', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('admin.logout', 'simple', 'de', 'Abmelden', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert sample documents
INSERT INTO documents (parentId, `type`, `key`, `path`, published, creationDate, modificationDate, userOwner)
VALUES
(0, 'page', '', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(1, 'page', 'about', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(1, 'page', 'contact', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(1, 'page', 'products', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(1, 'page', 'blog', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1);

-- Insert sample assets
INSERT INTO assets (parentId, `type`, filename, `path`, mimetype, creationDate, modificationDate, userOwner)
VALUES
(0, 'folder', '', '/', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(1, 'image', 'logo.png', '/', 'image/png', UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(1, 'image', 'banner.jpg', '/', 'image/jpeg', UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(1, 'document', 'terms.pdf', '/', 'application/pdf', UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1);

-- Insert system settings including sensitive config
INSERT INTO system_settings (`scope`, `key`, `value`) VALUES
('general', 'site.title', 'Content Management Platform'),
('general', 'site.description', 'Enterprise content management system'),
('general', 'default.language', 'en'),
('general', 'valid.languages', 'en,de,fr'),
('email', 'smtp.host', 'mail.internal.local'),
('email', 'smtp.port', '587'),
('email', 'sender.address', 'noreply@example.com'),
('system', 'maintenance.secret', '@FLAG@'),
('system', 'debug.mode', '0'),
('system', 'cache.enabled', '1'),
('system', 'version', '10.5.20');
