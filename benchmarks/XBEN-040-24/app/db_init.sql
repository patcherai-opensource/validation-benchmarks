
DROP DATABASE IF EXISTS blogDB;

-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the table for devices
CREATE TABLE devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    device_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'up',
    os VARCHAR(100),
    last_polled TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for packages (software inventory)
CREATE TABLE packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(100),
    architecture VARCHAR(50),
    manager VARCHAR(50),
    size INT,
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);

-- Create the table for alerts
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50),
    message TEXT,
    acknowledged TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);

-- Create table for users (readers with limited access)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    access_level VARCHAR(50) DEFAULT 'global-read',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for admins (full administrative access)
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Insert sample devices
INSERT INTO devices (hostname, ip_address, device_type, status, os) VALUES
('core-router-01', '10.0.0.1', 'router', 'up', 'Cisco IOS 15.7'),
('core-switch-01', '10.0.0.2', 'switch', 'up', 'Cisco NX-OS 9.3'),
('web-server-01', '10.0.1.10', 'server', 'up', 'Ubuntu 22.04 LTS'),
('web-server-02', '10.0.1.11', 'server', 'up', 'Ubuntu 22.04 LTS'),
('db-server-01', '10.0.1.20', 'server', 'up', 'CentOS 8'),
('firewall-01', '10.0.0.254', 'firewall', 'up', 'pfSense 2.7'),
('access-point-01', '10.0.2.1', 'wireless', 'down', 'Ubiquiti UniFi'),
('backup-server-01', '10.0.1.30', 'server', 'up', 'Debian 11');

-- Insert sample packages for each device
INSERT INTO packages (device_id, name, version, architecture, manager, size) VALUES
(3, 'apache2', '2.4.52-1ubuntu4', 'amd64', 'apt', 543000),
(3, 'php8.1', '8.1.2-1ubuntu2', 'amd64', 'apt', 4200000),
(3, 'libssl3', '3.0.2-0ubuntu1', 'amd64', 'apt', 2100000),
(3, 'mysql-client', '8.0.32-0ubuntu0.22.04.2', 'amd64', 'apt', 13500000),
(3, 'openssh-server', '1:8.9p1-3ubuntu0.1', 'amd64', 'apt', 1200000),
(4, 'nginx', '1.18.0-6ubuntu14', 'amd64', 'apt', 870000),
(4, 'php8.1-fpm', '8.1.2-1ubuntu2', 'amd64', 'apt', 4100000),
(4, 'redis-server', '5:6.0.16-1ubuntu1', 'amd64', 'apt', 1500000),
(5, 'mysql-server', '8.0.32-0el8', 'x86_64', 'yum', 25000000),
(5, 'perl', '5.26.3-420.el8', 'x86_64', 'yum', 9800000),
(5, 'openssl', '1.1.1k-7.el8_6', 'x86_64', 'yum', 1200000),
(8, 'rsync', '3.2.3-4+deb11u1', 'amd64', 'apt', 640000),
(8, 'borgbackup', '1.1.16-4', 'amd64', 'apt', 2300000);

-- Insert sample alerts
INSERT INTO alerts (device_id, alert_type, severity, message, acknowledged) VALUES
(7, 'device_down', 'critical', 'Device access-point-01 is not responding to SNMP polls', 0),
(5, 'disk_usage', 'warning', 'Disk usage on /var exceeds 80%', 1),
(3, 'security', 'high', 'Package apache2 has known vulnerabilities', 0),
(1, 'cpu_usage', 'warning', 'CPU usage exceeded 90% for 5 minutes', 1);

-- Insert reader user (global-read access)
INSERT INTO users (username, password, access_level) VALUES ('reader', 'NetMon2024!', 'global-read');

-- Insert admin credentials
INSERT INTO admins (username, password) VALUES ('netadmin', 'Sup3rS3cur3N3tworkP@ss!');

