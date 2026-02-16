-- Multi-Site CMS Database Schema

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

-- CMS member accounts
DROP TABLE IF EXISTS `cms_members`;
CREATE TABLE `cms_members` (
   `id` int NOT NULL AUTO_INCREMENT,
   `username` varchar(100) NOT NULL,
   `password_hash` varchar(255) NOT NULL,
   `email` varchar(255) DEFAULT NULL,
   `role` varchar(50) NOT NULL DEFAULT 'editor',
   `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`id`),
   UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `cms_members` (`username`, `password_hash`, `email`, `role`) VALUES
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin@cms.local', 'administrator'),
('editor', '$2y$10$5Q/DENrxDkm6VjbMpBj0Bel0xgq5Apz5KsuphL2c96VmTXHFANK52', 'editor@cms.local', 'editor');

-- Subsites (multi-site management)
DROP TABLE IF EXISTS `subsites`;
CREATE TABLE `subsites` (
   `id` int NOT NULL AUTO_INCREMENT,
   `title` varchar(255) NOT NULL,
   `domain` varchar(255) DEFAULT NULL,
   `is_primary` tinyint(1) NOT NULL DEFAULT 0,
   `language` varchar(10) DEFAULT 'en_US',
   `theme` varchar(100) DEFAULT 'default',
   `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `subsites` (`title`, `domain`, `is_primary`, `language`, `theme`) VALUES
('Main Site', 'www.example.com', 1, 'en_US', 'default'),
('Blog', 'blog.example.com', 0, 'en_US', 'developer'),
('Documentation', 'docs.example.com', 0, 'en_US', 'developer'),
('Store', 'store.example.com', 0, 'en_US', 'starter');

-- Access groups
DROP TABLE IF EXISTS `access_groups`;
CREATE TABLE `access_groups` (
   `id` int NOT NULL AUTO_INCREMENT,
   `title` varchar(255) NOT NULL,
   `access_all_sites` tinyint(1) NOT NULL DEFAULT 0,
   `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `access_groups` (`title`, `access_all_sites`) VALUES
('Administrators', 1),
('Content Editors', 0),
('Blog Authors', 0),
('Store Managers', 0);

-- Group-subsite many-many relationship
DROP TABLE IF EXISTS `group_subsites`;
CREATE TABLE `group_subsites` (
   `id` int NOT NULL AUTO_INCREMENT,
   `group_id` int NOT NULL,
   `subsite_id` int NOT NULL,
   PRIMARY KEY (`id`),
   KEY `group_id` (`group_id`),
   KEY `subsite_id` (`subsite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `group_subsites` (`group_id`, `subsite_id`) VALUES
(2, 1), (2, 2), (2, 3),
(3, 2),
(4, 4);

-- Member-group associations
DROP TABLE IF EXISTS `member_groups`;
CREATE TABLE `member_groups` (
   `id` int NOT NULL AUTO_INCREMENT,
   `member_id` int NOT NULL,
   `group_id` int NOT NULL,
   PRIMARY KEY (`id`),
   KEY `member_id` (`member_id`),
   KEY `group_id` (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `member_groups` (`member_id`, `group_id`) VALUES
(1, 1),
(2, 2), (2, 3);

-- Schema configuration: maps entity class names to table names
-- Used by the ORM layer for table resolution during migrations
DROP TABLE IF EXISTS `schema_config`;
CREATE TABLE `schema_config` (
   `id` int NOT NULL AUTO_INCREMENT,
   `class_name` varchar(255) NOT NULL,
   `table_name` varchar(255) NOT NULL,
   PRIMARY KEY (`id`),
   UNIQUE KEY `class_name` (`class_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `schema_config` (`class_name`, `table_name`) VALUES
('AccessGroup', 'access_groups'),
('Subsite', 'subsites'),
('Member', 'cms_members'),
('SubsiteDomain', 'subsites');

-- Internal system configuration store
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
   `id` int NOT NULL AUTO_INCREMENT,
   `config_key` varchar(255) NOT NULL,
   `config_value` text,
   PRIMARY KEY (`id`),
   UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `system_config` (`config_key`, `config_value`) VALUES
('site_title', 'Multi-Site CMS'),
('admin_email', 'admin@cms.local'),
('maintenance_mode', '0'),
('secret_token', '${FLAG}'),
('api_version', '2.1.0');
