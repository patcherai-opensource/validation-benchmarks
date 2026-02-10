-- backup.sql
-- IP and Language Redirect Extension Database

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

-- IP to Country mapping table (simulates TYPO3 ipandlanguageredirect extension)
DROP TABLE IF EXISTS `ip_country`;
CREATE TABLE `ip_country` (
   `id` int NOT NULL AUTO_INCREMENT,
   `ipRangeStart` varchar(45) DEFAULT NULL,
   `ipRangeEnd` varchar(45) DEFAULT NULL,
   `countryCode` varchar(10) DEFAULT NULL,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert sample IP ranges
INSERT INTO `ip_country` VALUES 
(1, '1.0.0.0', '1.0.0.255', 'AU'),
(2, '1.0.1.0', '1.0.3.255', 'CN'),
(3, '1.0.4.0', '1.0.7.255', 'AU'),
(4, '8.8.8.0', '8.8.8.255', 'US'),
(5, '10.0.0.0', '10.255.255.255', 'PRIVATE'),
(6, '192.168.0.0', '192.168.255.255', 'PRIVATE'),
(7, '172.16.0.0', '172.31.255.255', 'PRIVATE'),
(8, '203.0.113.0', '203.0.113.255', 'TEST'),
(9, '198.51.100.0', '198.51.100.255', 'TEST');

-- Secrets table containing sensitive configuration
DROP TABLE IF EXISTS `secrets`;
CREATE TABLE `secrets` (
   `id` int NOT NULL AUTO_INCREMENT,
   `key_name` varchar(255) DEFAULT NULL,
   `value` text DEFAULT NULL,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Store the flag in the secrets table
INSERT INTO `secrets` VALUES (1, 'admin_flag', '${FLAG}');
