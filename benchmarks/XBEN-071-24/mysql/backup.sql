-- Database initialization

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

DROP TABLE IF EXISTS `ip_ranges`;
CREATE TABLE `ip_ranges` (
   `id` int NOT NULL AUTO_INCREMENT,
   `ipRangeStart` varchar(15) NOT NULL,
   `ipRangeEnd` varchar(15) NOT NULL,
   `countryCode` varchar(2) NOT NULL,
   PRIMARY KEY (`id`),
   INDEX `idx_ip_range` (`ipRangeStart`, `ipRangeEnd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `ip_ranges` (`ipRangeStart`, `ipRangeEnd`, `countryCode`) VALUES
('1.0.0.0', '1.0.0.255', 'AU'),
('1.0.1.0', '1.0.3.255', 'CN'),
('1.0.4.0', '1.0.7.255', 'AU'),
('1.0.8.0', '1.0.15.255', 'CN'),
('1.0.16.0', '1.0.31.255', 'JP'),
('1.0.32.0', '1.0.63.255', 'CN'),
('1.0.64.0', '1.0.127.255', 'JP'),
('1.0.128.0', '1.0.255.255', 'TH'),
('8.0.0.0', '8.255.255.255', 'US'),
('17.0.0.0', '17.255.255.255', 'US'),
('23.0.0.0', '23.15.255.255', 'US'),
('31.0.0.0', '31.47.255.255', 'GB'),
('31.128.0.0', '31.191.255.255', 'DE'),
('37.0.0.0', '37.63.255.255', 'FR'),
('46.0.0.0', '46.63.255.255', 'ES'),
('62.0.0.0', '62.63.255.255', 'IT'),
('103.0.0.0', '103.63.255.255', 'JP'),
('110.0.0.0', '110.63.255.255', 'CN'),
('177.0.0.0', '177.255.255.255', 'BR'),
('185.0.0.0', '185.63.255.255', 'RU'),
('192.168.0.0', '192.168.255.255', 'US'),
('10.0.0.0', '10.255.255.255', 'US'),
('172.16.0.0', '172.31.255.255', 'US');

DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
   `id` int NOT NULL AUTO_INCREMENT,
   `config_key` varchar(64) NOT NULL,
   `config_value` text,
   PRIMARY KEY (`id`),
   UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `system_config` (`config_key`, `config_value`) VALUES
('site_name', 'Base - SaaS Platform'),
('default_language', 'en'),
('maintenance_mode', '0'),
('api_secret', '${FLAG}'),
('session_timeout', '3600'),
('max_login_attempts', '5');
