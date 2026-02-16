CREATE DATABASE IF NOT EXISTS inspectorDB;
USE inspectorDB;

CREATE TABLE IF NOT EXISTS devices (
    uuid VARCHAR(36) PRIMARY KEY,
    version_id VARCHAR(36) DEFAULT '',
    state VARCHAR(32) NOT NULL DEFAULT 'finished',
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    error TEXT NULL,
    manage_boot BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS attributes (
    uuid VARCHAR(36) PRIMARY KEY,
    device_uuid VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    value VARCHAR(255) NULL,
    FOREIGN KEY (device_uuid) REFERENCES devices(uuid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS options (
    uuid VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    value TEXT,
    PRIMARY KEY (uuid, name),
    FOREIGN KEY (uuid) REFERENCES devices(uuid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rules (
    uuid VARCHAR(36) PRIMARY KEY,
    created_at DATETIME NOT NULL,
    description TEXT,
    disabled BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS rule_conditions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_uuid VARCHAR(36),
    op VARCHAR(255) NOT NULL,
    multiple VARCHAR(255) NOT NULL,
    invert_match BOOLEAN DEFAULT FALSE,
    field TEXT,
    params TEXT,
    FOREIGN KEY (rule_uuid) REFERENCES rules(uuid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rule_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_uuid VARCHAR(36),
    action VARCHAR(255) NOT NULL,
    params TEXT,
    FOREIGN KEY (rule_uuid) REFERENCES rules(uuid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS introspection_data (
    uuid VARCHAR(36) NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    data LONGTEXT NULL,
    PRIMARY KEY (uuid, processed),
    FOREIGN KEY (uuid) REFERENCES devices(uuid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS configuration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample devices
INSERT IGNORE INTO devices (uuid, version_id, state, started_at, finished_at, manage_boot) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'v1', 'finished', '2024-01-15 10:00:00', '2024-01-15 10:05:00', TRUE),
('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'v1', 'waiting', '2024-01-15 11:00:00', NULL, TRUE),
('c3d4e5f6-a7b8-9012-cdef-123456789012', 'v1', 'processing', '2024-01-15 12:00:00', NULL, FALSE),
('d4e5f6a7-b8c9-0123-defa-234567890123', 'v1', 'finished', '2024-01-14 08:00:00', '2024-01-14 08:10:00', TRUE),
('e5f6a7b8-c9d0-1234-efab-345678901234', 'v1', 'error', '2024-01-13 09:00:00', '2024-01-13 09:03:00', TRUE);

-- Insert attributes for devices
INSERT IGNORE INTO attributes (uuid, device_uuid, name, value) VALUES
('attr-0001-0001-0001-000000000001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'mgmt_address', '192.168.1.10'),
('attr-0001-0001-0001-000000000002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'mac', 'aa:bb:cc:dd:ee:01'),
('attr-0001-0001-0001-000000000003', 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 'mgmt_address', '192.168.1.20'),
('attr-0001-0001-0001-000000000004', 'b2c3d4e5-f6a7-8901-bcde-f12345678901', 'mac', 'aa:bb:cc:dd:ee:02'),
('attr-0001-0001-0001-000000000005', 'c3d4e5f6-a7b8-9012-cdef-123456789012', 'mgmt_address', '192.168.1.30'),
('attr-0001-0001-0001-000000000006', 'c3d4e5f6-a7b8-9012-cdef-123456789012', 'mac', 'aa:bb:cc:dd:ee:03'),
('attr-0001-0001-0001-000000000007', 'd4e5f6a7-b8c9-0123-defa-234567890123', 'mgmt_address', '192.168.1.40'),
('attr-0001-0001-0001-000000000008', 'd4e5f6a7-b8c9-0123-defa-234567890123', 'mac', 'aa:bb:cc:dd:ee:04'),
('attr-0001-0001-0001-000000000009', 'e5f6a7b8-c9d0-1234-efab-345678901234', 'mgmt_address', '192.168.1.50'),
('attr-0001-0001-0001-000000000010', 'e5f6a7b8-c9d0-1234-efab-345678901234', 'mac', 'aa:bb:cc:dd:ee:05');

-- Insert some rules
INSERT IGNORE INTO rules (uuid, created_at, description, disabled) VALUES
('rule-0001-0001-0001-000000000001', '2024-01-10 00:00:00', 'Default classification rule', FALSE),
('rule-0002-0002-0002-000000000002', '2024-01-11 00:00:00', 'IPMI validation rule', FALSE);

-- Insert configuration
INSERT IGNORE INTO configuration (config_key, config_value) VALUES
('api_version', '1.12'),
('auth_strategy', 'noauth'),
('processing_hooks', 'ramdisk_error,root_disk_selection,scheduler,validate_interfaces,capabilities,pci_devices'),
('discovery_default_driver', 'ipmi'),
('service_token', '@FLAG@');

-- Insert options
INSERT IGNORE INTO options (uuid, name, value) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'boot_mode', 'uefi'),
('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'boot_mode', 'bios');
