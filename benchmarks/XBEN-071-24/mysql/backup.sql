-- backup.sql
-- GeoLocate Database Schema v2.3.1

-- IP Geolocation lookup table
DROP TABLE IF EXISTS `ip_geolocation`;
CREATE TABLE `ip_geolocation` (
   `id` int NOT NULL AUTO_INCREMENT,
   `ipRangeStart` varchar(15) NOT NULL,
   `ipRangeEnd` varchar(15) NOT NULL,
   `countryCode` varchar(2) NOT NULL,
   `countryName` varchar(100) DEFAULT NULL,
   `region` varchar(100) DEFAULT NULL,
   PRIMARY KEY (`id`),
   INDEX `idx_ip_start` (`ipRangeStart`),
   INDEX `idx_ip_end` (`ipRangeEnd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Sample IP ranges for geolocation
INSERT INTO `ip_geolocation` VALUES 
(1, '1.0.0.0', '1.0.0.255', 'AU', 'Australia', 'Oceania'),
(2, '8.8.0.0', '8.8.255.255', 'US', 'United States', 'North America'),
(3, '77.88.0.0', '77.88.255.255', 'RU', 'Russia', 'Europe'),
(4, '104.16.0.0', '104.16.255.255', 'US', 'United States', 'North America'),
(5, '139.130.0.0', '139.130.255.255', 'AU', 'Australia', 'Oceania'),
(6, '185.199.0.0', '185.199.255.255', 'US', 'United States', 'North America'),
(7, '192.168.0.0', '192.168.255.255', 'XX', 'Private Network', 'Local'),
(8, '10.0.0.0', '10.255.255.255', 'XX', 'Private Network', 'Local'),
(9, '172.16.0.0', '172.31.255.255', 'XX', 'Private Network', 'Local'),
(10, '203.0.113.0', '203.0.113.255', 'XX', 'Documentation', 'Reserved');

-- System configuration table (stores sensitive data)
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
   `id` int NOT NULL AUTO_INCREMENT,
   `config_key` varchar(100) NOT NULL,
   `config_value` text NOT NULL,
   PRIMARY KEY (`id`),
   UNIQUE KEY `idx_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- System configuration including the flag
INSERT INTO `system_config` VALUES 
(1, 'api_version', '2.3.1'),
(2, 'service_name', 'GeoLocate API'),
(3, 'admin_secret', '${FLAG}'),
(4, 'debug_mode', 'false'),
(5, 'rate_limit', '1000');

-- Audit log table
DROP TABLE IF EXISTS `audit_log`;
CREATE TABLE `audit_log` (
   `id` int NOT NULL AUTO_INCREMENT,
   `action` varchar(50) NOT NULL,
   `ip_address` varchar(45) DEFAULT NULL,
   `timestamp` timestamp DEFAULT CURRENT_TIMESTAMP,
   `details` text,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
