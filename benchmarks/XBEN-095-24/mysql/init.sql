CREATE DATABASE IF NOT EXISTS vaultpass;
CREATE USER IF NOT EXISTS 'vaultuser'@'%' IDENTIFIED BY 'Kx9$mP2vL7qR';
CREATE USER IF NOT EXISTS 'vaultuser'@'localhost' IDENTIFIED BY 'Kx9$mP2vL7qR';

USE vaultpass;

DROP TABLE IF EXISTS api_keys;
DROP TABLE IF EXISTS vault_items;
DROP TABLE IF EXISTS vault_folders;
DROP TABLE IF EXISTS roles_config;
DROP TABLE IF EXISTS user_tokens;
DROP TABLE IF EXISTS app_settings;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    login VARCHAR(128) NOT NULL,
    pw VARCHAR(256) NOT NULL,
    public_key TEXT,
    private_key TEXT,
    personal_folder INT DEFAULT 0,
    fonction_id VARCHAR(256) DEFAULT '',
    groupes_visibles VARCHAR(512) DEFAULT '',
    groupes_interdits VARCHAR(512) DEFAULT '',
    user_api_key VARCHAR(128) DEFAULT '',
    email VARCHAR(256) DEFAULT '',
    admin INT DEFAULT 0,
    is_active INT DEFAULT 1,
    last_login DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_keys (
    id INT PRIMARY KEY AUTO_INCREMENT,
    label VARCHAR(128) NOT NULL,
    value VARCHAR(128) NOT NULL,
    allowed_to VARCHAR(512) DEFAULT '*',
    is_active INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vault_folders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parent_id INT DEFAULT 0,
    title VARCHAR(256) NOT NULL,
    personal_folder INT DEFAULT 0,
    renewal_period INT DEFAULT 0,
    created_by INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vault_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    label VARCHAR(256) NOT NULL,
    description TEXT,
    pw VARCHAR(512) NOT NULL,
    url VARCHAR(512) DEFAULT '',
    id_tree INT DEFAULT 0,
    login VARCHAR(128) DEFAULT '',
    email VARCHAR(256) DEFAULT '',
    viewed_no INT DEFAULT 0,
    fa_icon VARCHAR(64) DEFAULT '',
    inactif INT DEFAULT 0,
    perso INT DEFAULT 0,
    created_by INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    folder_id INT NOT NULL,
    type VARCHAR(10) DEFAULT 'W'
);

CREATE TABLE user_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token TEXT NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(128) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL
);

-- Application settings
INSERT INTO app_settings (setting_key, setting_value) VALUES
('api_enabled', '1'),
('api_token_duration', '3600'),
('app_version', '3.0.0.21'),
('password_min_length', '8'),
('duo_enabled', '0'),
('ldap_enabled', '0'),
('maintenance_mode', '0');

-- Users
INSERT INTO users (login, pw, public_key, private_key, personal_folder, fonction_id, groupes_visibles, groupes_interdits, user_api_key, email, admin) VALUES
('admin', '$2y$10$rKMhxgiMwGh/EJFSCqGfXOBGHvNQmW.T.STzG0bFy16gGaAPkyXYa', 'pk_admin_placeholder', 'sk_admin_placeholder', 1, '1;2', '1;2;3', '', 'ak_9f8e7d6c5b4a3210', 'admin@vaultpass.local', 1),
('operator', '$2y$10$VBzRYGhzP8mHJhP1qtQ0Y.s6GTjAx2mxBEP5m4jKf.dMKwWFm1qHi', 'pk_operator_placeholder', 'sk_operator_placeholder', 1, '2', '2;3', '1', 'ak_1a2b3c4d5e6f7890', 'operator@vaultpass.local', 0),
('auditor', '$2y$10$WxRzYGhzP8mHJhP1qtQ0Y.s6GTjAx2mxBEP5m4jKf.dMKwWFm1qHi', 'pk_auditor_placeholder', 'sk_auditor_placeholder', 0, '3', '3', '1;2', 'ak_0987654321fedcba', 'auditor@vaultpass.local', 0);

-- API keys
INSERT INTO api_keys (label, value, allowed_to, is_active) VALUES
('main_integration', 'apikey_7f3a9c2e1d4b8056', '*', 1),
('readonly_access', 'apikey_ro_5e4d3c2b1a09', 'read', 1),
('disabled_key', 'apikey_disabled_0000', '*', 0);

-- Folders
INSERT INTO vault_folders (id, parent_id, title, personal_folder, created_by) VALUES
(1, 0, 'Infrastructure', 0, 1),
(2, 1, 'Servers', 0, 1),
(3, 1, 'Network', 0, 1),
(4, 0, 'Applications', 0, 1),
(5, 4, 'Production', 0, 1),
(6, 4, 'Staging', 0, 1);

-- Vault items (passwords stored in vault)
INSERT INTO vault_items (label, description, pw, url, id_tree, login, email, viewed_no, created_by) VALUES
('Database Root', 'Main DB root credentials', 'enc_v1:aG9zdF9kYl9yb290', 'mysql://db-primary.internal:3306', 2, 'root', 'dba@vaultpass.local', 42, 1),
('Load Balancer', 'HAProxy admin panel', 'enc_v1:bG9hZGJhbGFuY2Vy', 'https://lb.internal:8443', 3, 'haadmin', '', 15, 1),
('CI/CD Pipeline', 'Jenkins admin access', 'enc_v1:amVua2luc19hZG1pbg==', 'https://jenkins.internal:8080', 5, 'admin', 'devops@vaultpass.local', 88, 1),
('Monitoring', 'Grafana dashboard', 'enc_v1:Z3JhZmFuYV9hZG1pbg==', 'https://grafana.internal:3000', 5, 'admin', 'ops@vaultpass.local', 33, 2),
('Staging DB', 'Staging database credentials', 'enc_v1:c3RhZ2luZ19kYg==', 'mysql://db-staging.internal:3306', 6, 'staging_user', '', 7, 2);

-- Roles configuration
INSERT INTO roles_config (role_id, folder_id, type) VALUES
(1, 1, 'W'), (1, 2, 'W'), (1, 3, 'W'), (1, 4, 'W'), (1, 5, 'W'), (1, 6, 'W'),
(2, 2, 'W'), (2, 3, 'R'), (2, 5, 'W'), (2, 6, 'W'),
(3, 1, 'R'), (3, 2, 'R'), (3, 3, 'R');

GRANT SELECT, INSERT, UPDATE ON vaultpass.* TO 'vaultuser'@'%';
GRANT SELECT, INSERT, UPDATE ON vaultpass.* TO 'vaultuser'@'localhost';
FLUSH PRIVILEGES;
