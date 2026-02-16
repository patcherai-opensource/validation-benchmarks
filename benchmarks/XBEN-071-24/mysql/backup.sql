-- ContentHub CMS Database Schema

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

-- Asset identifier registry (maps unique identifiers to internal objects)
DROP TABLE IF EXISTS `asset_identifiers`;
CREATE TABLE `asset_identifiers` (
   `identifier` varchar(255) NOT NULL,
   `item_id` int NOT NULL,
   `item_type` varchar(64) NOT NULL DEFAULT 'document',
   `instance_label` varchar(255) DEFAULT NULL,
   PRIMARY KEY (`identifier`),
   KEY `idx_item` (`item_id`, `item_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Settings store for configuration values
DROP TABLE IF EXISTS `settings_store`;
CREATE TABLE `settings_store` (
   `id` int NOT NULL AUTO_INCREMENT,
   `setting_key` varchar(255) NOT NULL,
   `setting_value` text,
   `setting_type` varchar(32) DEFAULT 'string',
   `scope` varchar(64) NOT NULL DEFAULT 'public',
   PRIMARY KEY (`id`),
   UNIQUE KEY `uk_key_scope` (`setting_key`, `scope`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Populate asset identifiers
LOCK TABLES `asset_identifiers` WRITE;
INSERT INTO `asset_identifiers` (`identifier`, `item_id`, `item_type`, `instance_label`) VALUES
('a3f7c8e1-92b4-4d6a-b5e0-1f8a2c3d4e5f', 1, 'document', 'Homepage Banner'),
('b8d2e4f6-1a3c-5b7d-9e0f-2a4b6c8d0e1f', 2, 'image', 'Team Photo Gallery'),
('c1e3f5a7-2b4d-6c8e-0f1a-3b5d7e9f1a2b', 3, 'document', 'Privacy Policy'),
('d4f6a8c0-3e5f-7a9b-1c2d-4e6f8a0b2c3d', 4, 'asset', 'Product Brochure PDF'),
('e7a9b1d3-4f60-8b2c-3d4e-5f7a9b1c3d5e', 5, 'image', 'Logo Assets Package'),
('f0b2d4e6-5a71-9c3d-4e5f-6a8b0c2d4e6f', 6, 'document', 'Annual Report 2024'),
('11c3e5f7-6b82-0d4e-5f6a-7b9c1d3e5f7a', 7, 'asset', 'Marketing Materials'),
('22d4f6a8-7c93-1e5f-6a7b-8c0d2e4f6a8b', 8, 'image', 'Office Interior Photos'),
('33e5a7b9-8d04-2f6a-7b8c-9d1e3f5a7b9c', 9, 'document', 'Employee Handbook'),
('44f6b8c0-9e15-3a7b-8c9d-0e2f4a6b8c0d', 10, 'asset', 'Brand Guidelines');
UNLOCK TABLES;

-- Populate settings store
LOCK TABLES `settings_store` WRITE;
INSERT INTO `settings_store` (`setting_key`, `setting_value`, `setting_type`, `scope`) VALUES
('site_name', 'ContentHub CMS', 'string', 'public'),
('site_description', 'Enterprise Content Management System', 'string', 'public'),
('default_language', 'en', 'string', 'public'),
('max_upload_size', '10485760', 'int', 'public'),
('maintenance_mode', '0', 'bool', 'public'),
('api_rate_limit', '100', 'int', 'public'),
('cdn_enabled', '1', 'bool', 'public'),
('system_secret', '${FLAG}', 'string', 'internal'),
('db_backup_schedule', '0 2 * * *', 'string', 'internal'),
('smtp_password', 'mailrelay_2024_prod', 'string', 'internal'),
('license_key', 'CH-ENT-2024-A9F3B7', 'string', 'internal');
UNLOCK TABLES;
