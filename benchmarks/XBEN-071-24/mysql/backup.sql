-- Database initialization script
-- Pimcore CMS schema

-- Contact form submissions
DROP TABLE IF EXISTS `contact`;
CREATE TABLE `contact` (
   `id` int NOT NULL AUTO_INCREMENT,
   `name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
   `phone` varchar(255) DEFAULT NULL,
   `subject` varchar(255) DEFAULT NULL,
   `message` varchar(255) DEFAULT NULL,
   `email` varchar(255) DEFAULT NULL,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- UUID registry for object tracking
DROP TABLE IF EXISTS `uuids`;
CREATE TABLE `uuids` (
   `uuid` varchar(36) NOT NULL,
   `itemId` int unsigned NOT NULL DEFAULT '0',
   `type` varchar(25) NOT NULL DEFAULT '',
   `instanceIdentifier` varchar(50) NOT NULL DEFAULT '',
   PRIMARY KEY (`uuid`),
   KEY `itemId` (`itemId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Documents table
DROP TABLE IF EXISTS `documents`;
CREATE TABLE `documents` (
   `id` int unsigned NOT NULL AUTO_INCREMENT,
   `parentId` int unsigned DEFAULT NULL,
   `type` enum('page','snippet','link','hardlink','folder','email') DEFAULT NULL,
   `key` varchar(255) DEFAULT '',
   `path` varchar(765) DEFAULT NULL,
   `index` int unsigned DEFAULT '0',
   `published` tinyint unsigned DEFAULT '1',
   `creationDate` int unsigned DEFAULT NULL,
   `modificationDate` int unsigned DEFAULT NULL,
   `userOwner` int unsigned DEFAULT NULL,
   `userModification` int unsigned DEFAULT NULL,
   PRIMARY KEY (`id`),
   KEY `parentId` (`parentId`),
   KEY `key` (`key`),
   KEY `path` (`path`(255)),
   KEY `published` (`published`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Assets table
DROP TABLE IF EXISTS `assets`;
CREATE TABLE `assets` (
   `id` int unsigned NOT NULL AUTO_INCREMENT,
   `parentId` int unsigned DEFAULT NULL,
   `type` varchar(20) DEFAULT NULL,
   `filename` varchar(255) DEFAULT '',
   `path` varchar(765) DEFAULT NULL,
   `mimetype` varchar(190) DEFAULT NULL,
   `filesize` bigint unsigned DEFAULT NULL,
   `creationDate` int unsigned DEFAULT NULL,
   `modificationDate` int unsigned DEFAULT NULL,
   `userOwner` int unsigned DEFAULT NULL,
   `userModification` int unsigned DEFAULT NULL,
   PRIMARY KEY (`id`),
   KEY `parentId` (`parentId`),
   KEY `filename` (`filename`),
   KEY `path` (`path`(255))
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Users table
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
   `id` int unsigned NOT NULL AUTO_INCREMENT,
   `parentId` int unsigned DEFAULT NULL,
   `name` varchar(50) DEFAULT NULL,
   `password` varchar(255) DEFAULT NULL,
   `firstname` varchar(255) DEFAULT NULL,
   `lastname` varchar(255) DEFAULT NULL,
   `email` varchar(255) DEFAULT NULL,
   `active` tinyint unsigned DEFAULT '1',
   `admin` tinyint unsigned DEFAULT '0',
   `language` varchar(10) DEFAULT 'en',
   PRIMARY KEY (`id`),
   UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Website settings
DROP TABLE IF EXISTS `website_settings`;
CREATE TABLE `website_settings` (
   `id` int unsigned NOT NULL AUTO_INCREMENT,
   `name` varchar(190) NOT NULL DEFAULT '',
   `type` enum('text','document','asset','object','bool') DEFAULT NULL,
   `data` text,
   `siteId` int unsigned DEFAULT NULL,
   `creationDate` int unsigned DEFAULT NULL,
   `modificationDate` int unsigned DEFAULT NULL,
   PRIMARY KEY (`id`),
   KEY `name` (`name`),
   KEY `siteId` (`siteId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Translations admin
DROP TABLE IF EXISTS `translations_admin`;
CREATE TABLE `translations_admin` (
   `key` varchar(190) NOT NULL DEFAULT '',
   `language` varchar(10) NOT NULL DEFAULT '',
   `text` text,
   `creationDate` int unsigned DEFAULT NULL,
   `modificationDate` int unsigned DEFAULT NULL,
   PRIMARY KEY (`key`, `language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert seed data

-- Admin user (password: admin123 - bcrypt hashed)
INSERT INTO `users` (`id`, `name`, `password`, `firstname`, `lastname`, `email`, `active`, `admin`) VALUES
(1, 'admin', '$2y$10$kRGjNqH8XkGk1RQMFM5HaOcQcLNqNqzRqLxPW5fAqGjNwzqXi3gO', 'System', 'Admin', 'admin@pimcore.local', 1, 1);

-- Root documents
INSERT INTO `documents` (`id`, `parentId`, `type`, `key`, `path`, `published`, `creationDate`, `modificationDate`, `userOwner`) VALUES
(1, 0, 'page', '', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(2, 1, 'page', 'home', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(3, 1, 'page', 'about', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(4, 1, 'page', 'contact', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(5, 1, 'page', 'blog', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(6, 1, 'page', 'services', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(7, 1, 'page', 'pricing', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(8, 1, 'folder', 'emails', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(9, 8, 'email', 'contact-notification', '/emails/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(10, 1, 'snippet', 'header', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(11, 1, 'snippet', 'footer', '/', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(12, 1, 'page', 'privacy-policy', '/', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1);

-- Root assets
INSERT INTO `assets` (`id`, `parentId`, `type`, `filename`, `path`, `mimetype`, `filesize`, `creationDate`, `modificationDate`, `userOwner`) VALUES
(1, 0, 'folder', '', '/', NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(2, 1, 'folder', 'images', '/', NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(3, 2, 'image', 'hero.png', '/images/', 'image/png', 245760, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(4, 2, 'image', 'logo-dark.svg', '/images/', 'image/svg+xml', 2048, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(5, 2, 'image', 'logo-light.svg', '/images/', 'image/svg+xml', 1984, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(6, 1, 'folder', 'documents', '/', NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(7, 6, 'document', 'terms.pdf', '/documents/', 'application/pdf', 524288, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1),
(8, 6, 'document', 'privacy.pdf', '/documents/', 'application/pdf', 389120, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1);

-- UUID records mapping objects to their UUIDs
INSERT INTO `uuids` (`uuid`, `itemId`, `type`, `instanceIdentifier`) VALUES
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 1, 'document', 'default'),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 2, 'document', 'default'),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 3, 'document', 'default'),
('d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80', 4, 'document', 'default'),
('e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8091', 5, 'document', 'default'),
('f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8091a2', 1, 'asset', 'default'),
('07b8c9d0-e1f2-4a3b-4c5d-6e7f8091a2b3', 2, 'asset', 'default'),
('18c9d0e1-f2a3-4b4c-5d6e-7f8091a2b3c4', 3, 'asset', 'default'),
('29d0e1f2-a3b4-4c5d-6e7f-8091a2b3c4d5', 4, 'asset', 'default'),
('3ae1f2a3-b4c5-4d6e-7f80-91a2b3c4d5e6', 5, 'asset', 'default'),
('4bf2a3b4-c5d6-4e7f-8091-a2b3c4d5e6f7', 6, 'asset', 'default'),
('5ca3b4c5-d6e7-4f80-91a2-b3c4d5e6f708', 7, 'asset', 'default'),
('6db4c5d6-e7f8-4091-a2b3-c4d5e6f70819', 8, 'asset', 'default'),
('7ec5d6e7-f809-41a2-b3c4-d5e6f708192a', 6, 'document', 'default'),
('8fd6e7f8-091a-42b3-c4d5-e6f708192a3b', 7, 'document', 'default');

-- Website settings (includes sensitive configuration)
INSERT INTO `website_settings` (`id`, `name`, `type`, `data`, `siteId`, `creationDate`, `modificationDate`) VALUES
(1, 'website_title', 'text', 'Base - Modern SaaS Platform', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 'contact_email', 'text', 'info@base-saas.com', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 'google_analytics_id', 'text', 'UA-000000-1', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(4, 'maintenance_mode', 'bool', '0', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(5, 'api_secret_key', 'text', '${FLAG}', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(6, 'smtp_host', 'text', 'mail.base-saas.com', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(7, 'smtp_port', 'text', '587', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(8, 'default_language', 'text', 'en', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(9, 'recaptcha_site_key', 'text', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(10, 'cdn_url', 'text', 'https://cdn.base-saas.com', NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Admin translations
INSERT INTO `translations_admin` (`key`, `language`, `text`, `creationDate`, `modificationDate`) VALUES
('dashboard', 'en', 'Dashboard', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('assets', 'en', 'Assets', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('documents', 'en', 'Documents', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('settings', 'en', 'Settings', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('uuid_registry', 'en', 'UUID Registry', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('dashboard', 'de', 'Dashboard', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('assets', 'de', 'Medien', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('documents', 'de', 'Dokumente', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('settings', 'de', 'Einstellungen', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('uuid_registry', 'de', 'UUID-Registrierung', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());
