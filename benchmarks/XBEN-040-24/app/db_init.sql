
DROP DATABASE IF EXISTS netmonDB;

-- Create the database
CREATE DATABASE IF NOT EXISTS netmonDB;
USE netmonDB;

-- Create the table for monitored devices
CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    os_version VARCHAR(100),
    last_polled TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for installed packages (like LibreNMS)
CREATE TABLE packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(100),
    architecture VARCHAR(50) DEFAULT 'x86_64',
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Create the table for users (replacing admins)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for alerts
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT,
    alert_type VARCHAR(100),
    message TEXT,
    severity VARCHAR(50) DEFAULT 'warning',
    acknowledged TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Insert sample devices
INSERT INTO devices (hostname, ip_address, status, os_version) VALUES
('web-server-01', '192.168.1.10', 'active', 'Ubuntu 22.04 LTS'),
('db-server-01', '192.168.1.20', 'active', 'CentOS 8'),
('app-server-01', '192.168.1.30', 'active', 'Debian 11'),
('mail-server-01', '192.168.1.40', 'inactive', 'Ubuntu 20.04 LTS'),
('backup-server-01', '192.168.1.50', 'active', 'Rocky Linux 9'),
('monitor-server-01', '192.168.1.60', 'active', 'Ubuntu 22.04 LTS');

-- Insert sample packages
INSERT INTO packages (device_id, name, version, architecture) VALUES
(1, 'apache2', '2.4.52', 'x86_64'),
(1, 'php8.1', '8.1.2', 'x86_64'),
(1, 'libssl3', '3.0.2', 'x86_64'),
(1, 'openssl', '3.0.2', 'x86_64'),
(2, 'mysql-server', '8.0.32', 'x86_64'),
(2, 'mysql-client', '8.0.32', 'x86_64'),
(2, 'libmysqlclient21', '8.0.32', 'x86_64'),
(3, 'nodejs', '18.14.0', 'x86_64'),
(3, 'npm', '9.3.1', 'x86_64'),
(3, 'python3', '3.10.6', 'x86_64'),
(4, 'postfix', '3.6.4', 'x86_64'),
(4, 'dovecot-core', '2.3.16', 'x86_64'),
(5, 'rsync', '3.2.3', 'x86_64'),
(5, 'borgbackup', '1.2.4', 'x86_64'),
(6, 'snmpd', '5.9.1', 'x86_64'),
(6, 'librenms', '24.3.0', 'x86_64'),
(6, 'rrdtool', '1.7.2', 'x86_64');

-- Insert users including admin
INSERT INTO users (username, password, role, email) VALUES 
('admin', 'N3tM0n_Adm1n_S3cr3t!', 'admin', 'admin@netmon.local'),
('viewer', 'viewer123', 'viewer', 'viewer@netmon.local'),
('operator', 'oper@tor456', 'operator', 'operator@netmon.local');

-- Insert sample alerts
INSERT INTO alerts (device_id, alert_type, message, severity, acknowledged) VALUES
(4, 'device_down', 'Mail server is not responding to SNMP polls', 'critical', 0),
(2, 'disk_usage', 'Disk usage on /var exceeds 80%', 'warning', 1),
(1, 'cpu_high', 'CPU utilization above 90% for 15 minutes', 'warning', 0);

