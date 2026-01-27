-- backup.sql
-- NetMonitor Database Schema

DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices` (
   `device_id` int NOT NULL AUTO_INCREMENT,
   `hostname` varchar(255) DEFAULT NULL,
   `sysName` varchar(255) DEFAULT NULL,
   `ip_address` varchar(45) DEFAULT NULL,
   `status` int DEFAULT 1,
   `os` varchar(128) DEFAULT NULL,
   PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `ports`;
CREATE TABLE `ports` (
   `port_id` int NOT NULL AUTO_INCREMENT,
   `device_id` int NOT NULL,
   `ifDescr` varchar(255) DEFAULT NULL,
   `ifPhysAddress` varchar(64) DEFAULT NULL,
   `ifOperStatus` varchar(32) DEFAULT 'up',
   `ifSpeed` bigint DEFAULT NULL,
   PRIMARY KEY (`port_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
   `user_id` int NOT NULL AUTO_INCREMENT,
   `username` varchar(64) NOT NULL,
   `password` varchar(255) NOT NULL,
   `realname` varchar(128) DEFAULT NULL,
   `level` int DEFAULT 1,
   PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
   `config_id` int NOT NULL AUTO_INCREMENT,
   `config_name` varchar(128) NOT NULL,
   `config_value` text,
   PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert sample network devices
INSERT INTO `devices` VALUES 
(1, 'core-router-01', 'core-router-01.internal', '10.0.0.1', 1, 'Cisco IOS'),
(2, 'switch-floor1', 'switch-floor1.internal', '10.0.1.1', 1, 'Cisco IOS'),
(3, 'switch-floor2', 'switch-floor2.internal', '10.0.2.1', 1, 'HP ProCurve'),
(4, 'firewall-main', 'firewall.internal', '10.0.0.254', 1, 'pfSense'),
(5, 'server-rack-sw', 'server-rack-sw.internal', '10.0.10.1', 0, 'Juniper');

-- Insert sample ports with MAC addresses
INSERT INTO `ports` VALUES
(1, 1, 'GigabitEthernet0/0', 'aa:bb:cc:dd:ee:01', 'up', 1000000000),
(2, 1, 'GigabitEthernet0/1', 'aa:bb:cc:dd:ee:02', 'up', 1000000000),
(3, 2, 'FastEthernet0/1', 'aa:bb:cc:11:22:33', 'up', 100000000),
(4, 2, 'FastEthernet0/2', 'aa:bb:cc:11:22:34', 'down', 100000000),
(5, 3, 'Port 1', 'de:ad:be:ef:ca:fe', 'up', 1000000000),
(6, 3, 'Port 2', 'de:ad:be:ef:00:01', 'up', 1000000000),
(7, 4, 'em0', 'ca:fe:ba:be:00:01', 'up', 1000000000),
(8, 5, 'ge-0/0/0', 'fe:ed:fa:ce:00:01', 'down', 10000000000);

-- Insert default user (viewer role)
INSERT INTO `users` VALUES
(1, 'viewer', '$2y$10$4Cf1J/d68Xz6yI87LfeL.OijcxqPCTFzlnTHmAXtdpC4Z/t0Ipx.i', 'Network Viewer', 1);

-- Store sensitive configuration (flag hidden here)
INSERT INTO `system_config` VALUES
(1, 'site_name', 'NetMonitor NMS'),
(2, 'auth_mechanism', 'local'),
(3, 'api_key', '${FLAG}');
