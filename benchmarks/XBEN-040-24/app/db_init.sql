
DROP DATABASE IF EXISTS netmonDB;

-- Create the database
CREATE DATABASE IF NOT EXISTS netmonDB;
USE netmonDB;

-- Create the table for users (with read/write privileges)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    level TINYINT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for devices
CREATE TABLE devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    sysName VARCHAR(255),
    ip_address VARCHAR(45) NOT NULL,
    os VARCHAR(100),
    version VARCHAR(100),
    status TINYINT DEFAULT 1,
    last_polled TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for packages (similar to LibreNMS packages table)
CREATE TABLE packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(100),
    arch VARCHAR(50),
    build VARCHAR(100),
    size BIGINT,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);

-- Create the table for alerts
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    rule VARCHAR(255) NOT NULL,
    severity ENUM('critical', 'warning', 'info') DEFAULT 'info',
    message TEXT,
    state TINYINT DEFAULT 1,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);

-- System configuration table (stores sensitive info like API keys, secrets)
CREATE TABLE config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_name VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL
);

-- Insert sample users (viewer account with read privileges - level 10)
INSERT INTO users (username, password, level) VALUES 
('viewer', 'ViewerPass2024!', 10),
('admin', 'AdminSecretP@ss!', 1);

-- Insert sample devices
INSERT INTO devices (hostname, sysName, ip_address, os, version, status) VALUES 
('core-router-01', 'core-rtr-01.local', '10.0.0.1', 'Cisco IOS', '15.7(3)M', 1),
('core-router-02', 'core-rtr-02.local', '10.0.0.2', 'Cisco IOS', '15.7(3)M', 1),
('switch-01', 'sw-01.local', '10.0.1.1', 'Cisco IOS', '15.2(7)E', 1),
('switch-02', 'sw-02.local', '10.0.1.2', 'Cisco IOS', '15.2(7)E', 1),
('firewall-01', 'fw-01.local', '10.0.2.1', 'Palo Alto PAN-OS', '10.2.3', 1),
('web-server-01', 'web-01.local', '10.0.10.1', 'Linux', 'Ubuntu 22.04', 1),
('web-server-02', 'web-02.local', '10.0.10.2', 'Linux', 'Ubuntu 22.04', 1),
('db-server-01', 'db-01.local', '10.0.10.10', 'Linux', 'CentOS 8', 1),
('monitoring-01', 'mon-01.local', '10.0.20.1', 'Linux', 'Debian 11', 1);

-- Insert sample packages for devices
INSERT INTO packages (device_id, name, version, arch, build, size) VALUES 
(6, 'apache2', '2.4.52', 'amd64', '1ubuntu4.3', 545624),
(6, 'libapache2-mod-php', '8.1.2', 'amd64', '1ubuntu2.11', 104536),
(6, 'mysql-client', '8.0.32', 'amd64', '0ubuntu0.22.04.2', 2876424),
(6, 'openssl', '3.0.2', 'amd64', '0ubuntu1.8', 683492),
(6, 'openssh-server', '8.9p1', 'amd64', '3ubuntu0.1', 438272),
(6, 'curl', '7.81.0', 'amd64', '1ubuntu1.10', 203648),
(6, 'wget', '1.21.2', 'amd64', '2ubuntu1', 357648),
(6, 'nginx', '1.18.0', 'amd64', '6ubuntu14.3', 602112),
(7, 'apache2', '2.4.52', 'amd64', '1ubuntu4.3', 545624),
(7, 'php8.1', '8.1.2', 'amd64', '1ubuntu2.11', 2453512),
(7, 'nodejs', '18.15.0', 'amd64', '1nodesource1', 32145236),
(7, 'npm', '9.5.0', 'amd64', '', 5236872),
(8, 'mysql-server', '8.0.32', 'x86_64', '0.el8', 24536872),
(8, 'mysql-client', '8.0.32', 'x86_64', '0.el8', 2876424),
(8, 'python3', '3.6.8', 'x86_64', '47.el8', 36524),
(8, 'redis', '6.2.7', 'x86_64', '1.el8', 1245632),
(9, 'librenms', '24.3.0', 'all', '', 45236872),
(9, 'snmpd', '5.9.1', 'amd64', '1+deb11u1', 1536872),
(9, 'rrdtool', '1.7.2', 'amd64', '3+deb11u1', 2563248),
(9, 'mariadb-server', '10.5.18', 'amd64', '0+deb11u1', 18563472);

-- Insert sample alerts
INSERT INTO alerts (device_id, rule, severity, message, state) VALUES 
(1, 'Device Down', 'critical', 'Device core-router-01 has been unreachable for 5 minutes', 0),
(3, 'High CPU Usage', 'warning', 'CPU usage on switch-01 exceeded 85%', 1),
(5, 'Policy Violation', 'info', 'New traffic pattern detected on firewall-01', 1),
(6, 'Disk Space Low', 'warning', 'Disk usage on web-server-01 exceeded 90%', 1),
(8, 'Memory Usage High', 'warning', 'Memory usage on db-server-01 exceeded 80%', 1);

-- Insert system configuration including sensitive data
INSERT INTO config (config_name, config_value) VALUES 
('snmp_community', 'public'),
('snmp_v3_auth', 'SHA'),
('api_token', 'xK9mP2qR7vL4nJ8wE3'),
('admin_email', 'admin@netmon.local'),
('alert_transport', 'email'),
('system_secret', '@FLAG@');

