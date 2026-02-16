DROP DATABASE IF EXISTS nmsdb;

CREATE DATABASE IF NOT EXISTS nmsdb;
USE nmsdb;

-- Users table for authentication
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(128) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    realname VARCHAR(128) DEFAULT '',
    email VARCHAR(128) DEFAULT '',
    level TINYINT(1) DEFAULT 1,
    enabled TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Devices table for monitored network equipment
CREATE TABLE devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    sysName VARCHAR(255) DEFAULT '',
    sysDescr TEXT DEFAULT NULL,
    os VARCHAR(64) DEFAULT 'generic',
    hardware VARCHAR(255) DEFAULT '',
    version VARCHAR(255) DEFAULT '',
    ip VARCHAR(64) DEFAULT '',
    status TINYINT(1) DEFAULT 1,
    uptime BIGINT DEFAULT 0,
    last_polled TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ports/interfaces table
CREATE TABLE ports (
    port_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    ifIndex INT DEFAULT 0,
    ifDescr VARCHAR(255) DEFAULT '',
    ifAlias VARCHAR(255) DEFAULT '',
    ifType VARCHAR(64) DEFAULT '',
    ifPhysAddress VARCHAR(64) DEFAULT '',
    ifSpeed BIGINT DEFAULT 0,
    ifOperStatus VARCHAR(16) DEFAULT 'up',
    ifAdminStatus VARCHAR(16) DEFAULT 'up',
    ifInOctets BIGINT DEFAULT 0,
    ifOutOctets BIGINT DEFAULT 0,
    ifInErrors BIGINT DEFAULT 0,
    ifOutErrors BIGINT DEFAULT 0,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);

-- IPv4 addresses on ports
CREATE TABLE ipv4_addresses (
    ipv4_address_id INT AUTO_INCREMENT PRIMARY KEY,
    ipv4_address VARCHAR(64) NOT NULL,
    ipv4_prefixlen INT DEFAULT 24,
    port_id INT NOT NULL,
    FOREIGN KEY (port_id) REFERENCES ports(port_id) ON DELETE CASCADE
);

-- Alert rules
CREATE TABLE alert_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL,
    rule_query TEXT,
    severity ENUM('critical','warning','info') DEFAULT 'warning',
    enabled TINYINT(1) DEFAULT 1
);

-- Alert log
CREATE TABLE alert_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    rule_id INT,
    device_id INT,
    state TINYINT(1) DEFAULT 0,
    details TEXT,
    time_logged TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event log
CREATE TABLE eventlog (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT DEFAULT NULL,
    reference VARCHAR(64) DEFAULT NULL,
    type VARCHAR(64) DEFAULT '',
    message TEXT,
    severity TINYINT(1) DEFAULT 2,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuration store (holds sensitive system configuration)
CREATE TABLE config_store (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    config_group VARCHAR(128) NOT NULL,
    config_name VARCHAR(128) NOT NULL,
    config_value TEXT NOT NULL,
    config_default TEXT DEFAULT '',
    config_descr VARCHAR(255) DEFAULT ''
);

-- Insert default user (password: monitoring2024)
INSERT INTO users (username, password_hash, realname, email, level) VALUES
('operator', '$2y$10$X1aCbnZvH.81cPJx9oBv3u4Zj1kFPOA0ygX/M5inqVHOk6hv9GFHC', 'Network Operator', 'operator@netmon.local', 1);

-- Insert admin user
INSERT INTO users (username, password_hash, realname, email, level) VALUES
('admin', '$2y$10$rNGnwPA09JnPRJ12DbZa4OvJwn3rrhhOlIxkJrppgA6RGhw/CgXjW', 'System Administrator', 'admin@netmon.local', 10);

-- Insert configuration entries
INSERT INTO config_store (config_group, config_name, config_value, config_default, config_descr) VALUES
('snmp', 'community_ro', 'public', 'public', 'Default SNMP read community string'),
('snmp', 'community_rw', 'private', 'private', 'Default SNMP write community string'),
('snmp', 'version', 'v2c', 'v2c', 'Default SNMP version'),
('system', 'base_url', 'http://localhost', 'http://localhost', 'Base URL for the monitoring system'),
('system', 'admin_token', '@FLAG@', '', 'Internal system API token'),
('alerting', 'email_enabled', '1', '0', 'Enable email alerting'),
('alerting', 'email_from', 'nms@netmon.local', '', 'From address for alert emails');

-- Insert sample devices
INSERT INTO devices (hostname, sysName, sysDescr, os, hardware, version, ip, status, uptime) VALUES
('core-sw01.dc1.local', 'core-sw01', 'Cisco IOS Software, C3750E Software (C3750E-UNIVERSALK9-M), Version 15.2(4)E10', 'ios', 'WS-C3750X-48PF', '15.2(4)E10', '10.1.1.1', 1, 8640000),
('core-sw02.dc1.local', 'core-sw02', 'Cisco IOS Software, C3750E Software (C3750E-UNIVERSALK9-M), Version 15.2(4)E10', 'ios', 'WS-C3750X-48PF', '15.2(4)E10', '10.1.1.2', 1, 7200000),
('dist-sw01.dc1.local', 'dist-sw01', 'Cisco NX-OS(tm) n5000, Software (n5000-uk9), Version 7.3(8)N1(1)', 'nxos', 'N5K-C5672UP', '7.3(8)N1(1)', '10.1.2.1', 1, 4320000),
('fw01.dc1.local', 'fw01', 'Palo Alto Networks PA-3260 series, PAN-OS 10.2.5', 'panos', 'PA-3260', '10.2.5', '10.1.0.1', 1, 12960000),
('ap-controller.dc1.local', 'ap-ctrl', 'Aruba JL086A 3810M-40G-8SR PoE+ Switch, revision KB.16.10.0013', 'arubaos', 'JL086A', 'KB.16.10', '10.1.3.1', 1, 2592000),
('linux-srv01.dc1.local', 'linux-srv01', 'Linux linux-srv01 5.15.0-91-generic #101-Ubuntu SMP x86_64', 'linux', 'PowerEdge R640', '5.15.0-91', '10.1.10.5', 1, 1728000),
('linux-srv02.dc1.local', 'linux-srv02', 'Linux linux-srv02 5.15.0-91-generic #101-Ubuntu SMP x86_64', 'linux', 'PowerEdge R740', '5.15.0-91', '10.1.10.6', 0, 0),
('edge-rtr01.dc1.local', 'edge-rtr01', 'Juniper Networks, Inc. mx240 internet router, kernel JUNOS 21.4R3-S5', 'junos', 'MX240', '21.4R3-S5', '10.1.0.254', 1, 17280000),
('ups01.dc1.local', 'ups01', 'APC Web/SNMP Management Card (MB:v4.1.0 PF:v6.9.6)', 'apc', 'AP9631', 'v6.9.6', '10.1.0.10', 1, 25920000),
('printer01.office.local', 'printer01', 'HP ETHERNET MULTI-ENVIRONMENT', 'printer', 'HP LaserJet M609', '', '10.1.20.50', 1, 864000);

-- Insert ports/interfaces
INSERT INTO ports (device_id, ifIndex, ifDescr, ifAlias, ifType, ifPhysAddress, ifSpeed, ifOperStatus, ifAdminStatus, ifInOctets, ifOutOctets, ifInErrors, ifOutErrors) VALUES
(1, 1, 'GigabitEthernet1/0/1', 'Uplink to core-sw02', 'ethernetCsmacd', '001a2b3c4d01', 1000000000, 'up', 'up', 584729104832, 293847561024, 0, 0),
(1, 2, 'GigabitEthernet1/0/2', 'To dist-sw01', 'ethernetCsmacd', '001a2b3c4d02', 1000000000, 'up', 'up', 193847560128, 97283745024, 0, 0),
(1, 3, 'GigabitEthernet1/0/3', 'To fw01', 'ethernetCsmacd', '001a2b3c4d03', 1000000000, 'up', 'up', 87294710528, 43827103256, 12, 3),
(1, 10, 'Vlan1', 'Management VLAN', 'propVirtual', '001a2b3c4d00', 0, 'up', 'up', 482910, 291048, 0, 0),
(2, 1, 'GigabitEthernet1/0/1', 'Uplink to core-sw01', 'ethernetCsmacd', '001a2b3c4e01', 1000000000, 'up', 'up', 293847561024, 584729104832, 0, 0),
(2, 2, 'GigabitEthernet1/0/2', 'To dist-sw01 secondary', 'ethernetCsmacd', '001a2b3c4e02', 1000000000, 'up', 'up', 97283745024, 193847560128, 0, 0),
(2, 3, 'GigabitEthernet1/0/3', 'Server farm link', 'ethernetCsmacd', '001a2b3c4e03', 10000000000, 'up', 'up', 2948271046528, 1827365012480, 0, 0),
(3, 1, 'Ethernet1/1', 'Uplink to core-sw01', 'ethernetCsmacd', '00ab4c7d8e01', 10000000000, 'up', 'up', 1293847560128, 897283745024, 0, 0),
(3, 2, 'Ethernet1/2', 'Uplink to core-sw02', 'ethernetCsmacd', '00ab4c7d8e02', 10000000000, 'up', 'up', 1197283745024, 793847560128, 0, 0),
(3, 3, 'Ethernet1/3', 'Access segment A', 'ethernetCsmacd', '00ab4c7d8e03', 1000000000, 'up', 'up', 48293710528, 29384712048, 0, 0),
(4, 1, 'ethernet1/1', 'WAN link ISP-A', 'ethernetCsmacd', '00cc5d6e7f01', 1000000000, 'up', 'up', 87294710528, 43827103256, 0, 0),
(4, 2, 'ethernet1/2', 'LAN trunk', 'ethernetCsmacd', '00cc5d6e7f02', 10000000000, 'up', 'up', 584729104832, 293847561024, 0, 0),
(4, 3, 'ethernet1/3', 'DMZ segment', 'ethernetCsmacd', '00cc5d6e7f03', 1000000000, 'up', 'up', 29384756102, 14829371048, 3, 0),
(5, 1, 'GigabitEthernet0/0/1', 'AP uplink', 'ethernetCsmacd', '00de6e8f9a01', 1000000000, 'up', 'up', 97283745024, 48293710528, 0, 0),
(5, 2, 'GigabitEthernet0/0/2', 'Management', 'ethernetCsmacd', '00de6e8f9a02', 1000000000, 'up', 'up', 4829371, 2938471, 0, 0),
(6, 1, 'eth0', 'Management interface', 'ethernetCsmacd', '0a1b2c3d4e5f', 1000000000, 'up', 'up', 2948271046528, 1827365012480, 0, 0),
(6, 2, 'eth1', 'Application network', 'ethernetCsmacd', '0a1b2c3d4e60', 10000000000, 'up', 'up', 19384756012800, 9827365012480, 0, 0),
(7, 1, 'eth0', 'Management interface', 'ethernetCsmacd', '0a1b2c3d4e61', 1000000000, 'down', 'up', 0, 0, 0, 0),
(8, 1, 'ge-0/0/0', 'WAN ISP-A', 'ethernetCsmacd', '00ef7f0a1b01', 10000000000, 'up', 'up', 87294710528000, 43827103256000, 0, 0),
(8, 2, 'ge-0/0/1', 'WAN ISP-B', 'ethernetCsmacd', '00ef7f0a1b02', 10000000000, 'up', 'up', 43827103256000, 29384756102000, 0, 0),
(8, 3, 'ge-0/0/2', 'LAN core', 'ethernetCsmacd', '00ef7f0a1b03', 10000000000, 'up', 'up', 584729104832000, 293847561024000, 0, 0),
(9, 1, 'mgmt0', 'UPS Management', 'ethernetCsmacd', '00fa8a1b2c01', 100000000, 'up', 'up', 482910, 291048, 0, 0),
(10, 1, 'eth0', 'Printer Network', 'ethernetCsmacd', '00fb9b2c3d01', 100000000, 'up', 'up', 4829100, 2910480, 0, 0);

-- Insert IPv4 addresses
INSERT INTO ipv4_addresses (ipv4_address, ipv4_prefixlen, port_id) VALUES
('10.1.1.1', 30, 1),
('10.1.1.5', 30, 2),
('10.1.1.9', 30, 3),
('10.1.1.254', 24, 4),
('10.1.1.2', 30, 5),
('10.1.1.6', 30, 6),
('10.1.2.1', 24, 8),
('10.1.0.1', 24, 11),
('10.1.0.2', 30, 12),
('10.1.3.1', 24, 14),
('10.1.10.5', 24, 16),
('10.1.10.6', 24, 18),
('10.1.0.254', 30, 19);

-- Insert some alert rules
INSERT INTO alert_rules (rule_name, rule_query, severity, enabled) VALUES
('Device Down', 'devices.status = 0', 'critical', 1),
('High CPU', 'processors.processor_usage > 90', 'warning', 1),
('Interface Errors', 'ports.ifInErrors > 100 OR ports.ifOutErrors > 100', 'warning', 1),
('Disk Usage Critical', 'storage.storage_perc > 95', 'critical', 1);

-- Insert some alert log entries
INSERT INTO alert_log (rule_id, device_id, state, details) VALUES
(1, 7, 1, 'Device linux-srv02.dc1.local is unreachable'),
(3, 1, 1, 'Interface GigabitEthernet1/0/3 has 12 input errors'),
(3, 4, 1, 'Interface ethernet1/3 has 3 input errors');

-- Insert some event log entries
INSERT INTO eventlog (device_id, reference, type, message, severity) VALUES
(1, NULL, 'system', 'Device polled successfully', 1),
(2, NULL, 'system', 'Device polled successfully', 1),
(7, NULL, 'system', 'Device unreachable - SNMP timeout', 4),
(3, NULL, 'interface', 'Interface Ethernet1/3 changed state to up', 2),
(4, NULL, 'system', 'Device polled successfully', 1),
(8, NULL, 'system', 'Device polled successfully', 1),
(1, NULL, 'interface', 'Interface GigabitEthernet1/0/3 has errors', 3),
(6, NULL, 'system', 'Device polled successfully', 1);

