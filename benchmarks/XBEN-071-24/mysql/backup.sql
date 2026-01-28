-- backup.sql
-- NetWatch Pro - Network Monitoring System Database Schema

-- Users table for authentication
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
   `id` int NOT NULL AUTO_INCREMENT,
   `username` varchar(50) NOT NULL,
   `password` varchar(255) NOT NULL,
   `email` varchar(100) DEFAULT NULL,
   `role` varchar(20) DEFAULT 'viewer',
   `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`id`),
   UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Network devices table
DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices` (
   `device_id` int NOT NULL AUTO_INCREMENT,
   `hostname` varchar(100) NOT NULL,
   `ip_address` varchar(45) DEFAULT NULL,
   `device_type` varchar(50) DEFAULT 'unknown',
   `location` varchar(100) DEFAULT NULL,
   `status` varchar(20) DEFAULT 'active',
   PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Network interfaces table with MAC addresses
DROP TABLE IF EXISTS `interfaces`;
CREATE TABLE `interfaces` (
   `interface_id` int NOT NULL AUTO_INCREMENT,
   `device_id` int NOT NULL,
   `ifName` varchar(50) DEFAULT NULL,
   `ifPhysAddress` varchar(17) DEFAULT NULL,
   `ifOperStatus` varchar(20) DEFAULT 'up',
   `ifSpeed` bigint DEFAULT 0,
   `ifDescr` varchar(255) DEFAULT NULL,
   PRIMARY KEY (`interface_id`),
   KEY `device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- System configuration/secrets table
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
   `config_id` int NOT NULL AUTO_INCREMENT,
   `config_key` varchar(100) NOT NULL,
   `config_value` varchar(255) DEFAULT NULL,
   `is_sensitive` tinyint(1) DEFAULT 0,
   PRIMARY KEY (`config_id`),
   UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert default user (viewer role)
INSERT INTO `users` (`username`, `password`, `email`, `role`) VALUES 
('viewer', 'viewer123', 'viewer@netwatch.local', 'viewer'),
('admin', 'sup3rs3cr3t!', 'admin@netwatch.local', 'admin');

-- Insert sample devices
INSERT INTO `devices` (`hostname`, `ip_address`, `device_type`, `location`, `status`) VALUES
('core-sw01', '10.0.1.1', 'switch', 'DC1-Rack01', 'active'),
('core-sw02', '10.0.1.2', 'switch', 'DC1-Rack02', 'active'),
('fw-edge01', '10.0.0.1', 'firewall', 'DC1-DMZ', 'active'),
('srv-web01', '10.0.10.10', 'server', 'DC1-Rack05', 'active'),
('srv-db01', '10.0.10.20', 'server', 'DC1-Rack06', 'active'),
('ap-floor1', '10.0.20.1', 'access_point', 'Building-A', 'active'),
('router-wan', '10.0.0.254', 'router', 'DC1-Edge', 'active');

-- Insert sample interfaces with MAC addresses
INSERT INTO `interfaces` (`device_id`, `ifName`, `ifPhysAddress`, `ifOperStatus`, `ifSpeed`, `ifDescr`) VALUES
(1, 'Gi0/1', '00:1A:2B:3C:4D:01', 'up', 1000000000, 'GigabitEthernet0/1 - Uplink'),
(1, 'Gi0/2', '00:1A:2B:3C:4D:02', 'up', 1000000000, 'GigabitEthernet0/2 - Server Link'),
(1, 'Gi0/24', '00:1A:2B:3C:4D:18', 'down', 1000000000, 'GigabitEthernet0/24 - Unused'),
(2, 'Gi0/1', '00:1A:2B:3C:4E:01', 'up', 1000000000, 'GigabitEthernet0/1 - Uplink'),
(2, 'Gi0/2', '00:1A:2B:3C:4E:02', 'up', 1000000000, 'GigabitEthernet0/2 - Firewall'),
(3, 'eth0', 'AA:BB:CC:DD:EE:01', 'up', 10000000000, 'External Interface'),
(3, 'eth1', 'AA:BB:CC:DD:EE:02', 'up', 10000000000, 'Internal Interface'),
(4, 'eth0', 'DE:AD:BE:EF:00:01', 'up', 10000000000, 'Primary NIC'),
(5, 'eth0', 'DE:AD:BE:EF:00:02', 'up', 10000000000, 'Primary NIC'),
(6, 'wlan0', 'CA:FE:BA:BE:00:01', 'up', 300000000, 'Wireless Radio'),
(7, 'Gi0/0', 'FA:CE:B0:0C:00:01', 'up', 1000000000, 'WAN Interface');

-- System configuration (flag stored here)
INSERT INTO `system_config` (`config_key`, `config_value`, `is_sensitive`) VALUES
('site_name', 'NetWatch Pro', 0),
('polling_interval', '300', 0),
('snmp_community', 'public', 1),
('api_secret_key', '${FLAG}', 1),
('db_backup_enabled', 'true', 0);
