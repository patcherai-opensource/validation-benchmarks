-- backup.sql
-- Network Device Management Database

-- Users table for authentication
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
   `user_id` int NOT NULL AUTO_INCREMENT,
   `username` varchar(128) NOT NULL,
   `password` varchar(255) NOT NULL,
   `realname` varchar(128) DEFAULT NULL,
   `email` varchar(255) DEFAULT NULL,
   `level` int DEFAULT 1,
   PRIMARY KEY (`user_id`),
   UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert default user (low privilege user as per CVE)
INSERT INTO `users` (username, password, realname, email, level) VALUES 
('operator', 'operator123', 'Network Operator', 'operator@local.net', 1),
('admin', 'admin_secure_pass_2024!', 'Administrator', 'admin@local.net', 10);

-- Devices table - network devices
DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices` (
   `device_id` int NOT NULL AUTO_INCREMENT,
   `hostname` varchar(255) DEFAULT NULL,
   `sysName` varchar(255) DEFAULT NULL,
   `ip` varchar(64) DEFAULT NULL,
   `status` tinyint DEFAULT 1,
   PRIMARY KEY (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert some network devices
INSERT INTO `devices` (hostname, sysName, ip, status) VALUES
('router-core-01', 'CORE-RTR-01', '192.168.1.1', 1),
('switch-access-01', 'ACC-SW-01', '192.168.1.10', 1),
('switch-access-02', 'ACC-SW-02', '192.168.1.11', 1),
('firewall-edge', 'FW-EDGE-01', '192.168.1.254', 1),
('server-dc-01', 'DC-SRV-01', '192.168.2.10', 1);

-- Interfaces table (ports) with MAC addresses - similar to LibreNMS ports table
DROP TABLE IF EXISTS `ports`;
CREATE TABLE `ports` (
   `port_id` int NOT NULL AUTO_INCREMENT,
   `device_id` int NOT NULL,
   `ifDescr` varchar(255) DEFAULT NULL,
   `ifName` varchar(128) DEFAULT NULL,
   `ifPhysAddress` varchar(64) DEFAULT NULL,
   `ifOperStatus` varchar(32) DEFAULT 'up',
   `ifSpeed` bigint DEFAULT NULL,
   PRIMARY KEY (`port_id`),
   KEY `device_id` (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert interface/port data with MAC addresses
INSERT INTO `ports` (device_id, ifDescr, ifName, ifPhysAddress, ifOperStatus, ifSpeed) VALUES
(1, 'GigabitEthernet0/0', 'Gi0/0', '00:1A:2B:3C:4D:5E', 'up', 1000000000),
(1, 'GigabitEthernet0/1', 'Gi0/1', '00:1A:2B:3C:4D:5F', 'up', 1000000000),
(2, 'FastEthernet0/1', 'Fa0/1', 'AA:BB:CC:DD:EE:01', 'up', 100000000),
(2, 'FastEthernet0/2', 'Fa0/2', 'AA:BB:CC:DD:EE:02', 'down', 100000000),
(3, 'FastEthernet0/1', 'Fa0/1', 'AA:BB:CC:DD:EE:11', 'up', 100000000),
(3, 'FastEthernet0/2', 'Fa0/2', 'AA:BB:CC:DD:EE:12', 'up', 100000000),
(4, 'eth0', 'eth0', '00:50:56:AA:BB:01', 'up', 1000000000),
(4, 'eth1', 'eth1', '00:50:56:AA:BB:02', 'up', 1000000000),
(5, 'ens192', 'ens192', '00:50:56:CC:DD:01', 'up', 10000000000);

-- Secrets table for storing sensitive data (flag stored here)
DROP TABLE IF EXISTS `secrets`;
CREATE TABLE `secrets` (
   `id` int NOT NULL AUTO_INCREMENT,
   `secret_name` varchar(128) DEFAULT NULL,
   `secret_value` varchar(255) DEFAULT NULL,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- El placeholder ${FLAG} será reemplazado en el script de inicialización
LOCK TABLES `secrets` WRITE;
INSERT INTO `secrets` (secret_name, secret_value) VALUES ('api_key', '${FLAG}');
UNLOCK TABLES;
