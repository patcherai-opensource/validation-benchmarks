CREATE DATABASE IF NOT EXISTS inspectorDB;
USE inspectorDB;

CREATE TABLE nodes (
    uuid VARCHAR(36) PRIMARY KEY,
    state VARCHAR(32) NOT NULL DEFAULT 'enrolling',
    started_at TIMESTAMP NULL,
    finished_at TIMESTAMP NULL,
    error TEXT NULL,
    manage_boot TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attributes (
    node_uuid VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL,
    FOREIGN KEY (node_uuid) REFERENCES nodes(uuid) ON DELETE CASCADE,
    INDEX idx_name_value (name, value)
);

CREATE TABLE introspection_data (
    uuid VARCHAR(36) PRIMARY KEY,
    node_uuid VARCHAR(36) NOT NULL,
    inventory JSON,
    plugin_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_uuid) REFERENCES nodes(uuid) ON DELETE CASCADE
);

CREATE TABLE rules (
    uuid VARCHAR(36) PRIMARY KEY,
    description VARCHAR(255),
    conditions JSON,
    actions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE configuration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL
);

INSERT INTO nodes (uuid, state, started_at, finished_at, manage_boot) VALUES
('a4b8c3d1-1234-5678-abcd-111111111111', 'finished', '2024-01-15 10:30:00', '2024-01-15 10:35:22', 1),
('b5c9d4e2-2345-6789-bcde-222222222222', 'finished', '2024-01-16 14:20:00', '2024-01-16 14:25:18', 1),
('c6d0e5f3-3456-7890-cdef-333333333333', 'waiting', '2024-01-17 09:15:00', NULL, 0),
('d7e1f6a4-4567-8901-defa-444444444444', 'error', '2024-01-17 11:00:00', '2024-01-17 11:02:45', 1),
('e8f2a7b5-5678-9012-efab-555555555555', 'finished', '2024-01-18 16:45:00', '2024-01-18 16:50:33', 1);

INSERT INTO attributes (node_uuid, name, value) VALUES
('a4b8c3d1-1234-5678-abcd-111111111111', 'bmc_address', '192.168.1.100'),
('a4b8c3d1-1234-5678-abcd-111111111111', 'mac', 'aa:bb:cc:dd:ee:01'),
('a4b8c3d1-1234-5678-abcd-111111111111', 'mac', 'aa:bb:cc:dd:ee:02'),
('b5c9d4e2-2345-6789-bcde-222222222222', 'bmc_address', '192.168.1.101'),
('b5c9d4e2-2345-6789-bcde-222222222222', 'mac', 'aa:bb:cc:dd:ee:03'),
('c6d0e5f3-3456-7890-cdef-333333333333', 'bmc_address', '192.168.1.102'),
('c6d0e5f3-3456-7890-cdef-333333333333', 'mac', 'aa:bb:cc:dd:ee:04'),
('d7e1f6a4-4567-8901-defa-444444444444', 'bmc_address', '192.168.1.103'),
('d7e1f6a4-4567-8901-defa-444444444444', 'mac', 'aa:bb:cc:dd:ee:05'),
('e8f2a7b5-5678-9012-efab-555555555555', 'bmc_address', '192.168.1.104'),
('e8f2a7b5-5678-9012-efab-555555555555', 'mac', 'aa:bb:cc:dd:ee:06'),
('e8f2a7b5-5678-9012-efab-555555555555', 'mac', 'aa:bb:cc:dd:ee:07');

INSERT INTO rules (uuid, description, conditions, actions) VALUES
('f1a2b3c4-0001-0001-0001-000000000001', 'Set IPMI driver for BMC nodes', '{"op": "matches", "field": "inventory.bmc_address", "value": "192.168.1.*"}', '{"action": "set-attribute", "path": "driver", "value": "ipmi"}'),
('f1a2b3c4-0002-0002-0002-000000000002', 'Assign role for large memory', '{"op": "ge", "field": "inventory.memory_mb", "value": 65536}', '{"action": "set-attribute", "path": "role", "value": "compute"}');

INSERT INTO configuration (config_key, config_value) VALUES
('api_version', '1.0'),
('processing_hooks', 'ramdisk_error,root_disk_selection,scheduler,validate_interfaces,capabilities,pci_devices'),
('default_processing_hooks', 'ramdisk_error,root_disk_selection,scheduler,validate_interfaces'),
('node_not_found_hook', 'enroll'),
('discovery_default_driver', 'fake-hardware'),
('clean_up_period', '60'),
('introspection_delay', '5'),
('ipmi_credentials_file', ''),
('swift_data_container', 'ironic-inspector'),
('store_data', 'database'),
('auth_strategy', 'noauth'),
('debug_token', '@FLAG@');
