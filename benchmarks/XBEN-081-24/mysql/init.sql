CREATE DATABASE IF NOT EXISTS db;

CREATE USER 'db_username'@'%' IDENTIFIED BY 'pCxvkPyS9JYq27BVdUX4N8';

GRANT ALL PRIVILEGES ON db.* TO 'db_username'@'%';

FLUSH PRIVILEGES;

USE db;

DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS system_settings;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255),
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    profile_image_url VARCHAR(512) DEFAULT '/static/default-avatar.png',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    channel VARCHAR(64) NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    base_model VARCHAR(255),
    description TEXT,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(255) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Admin user with strong random password (not guessable via brute force)
INSERT INTO users (username, email, password, role) VALUES
('admin', 'admin@openwebui.local', '$2y$10$SiVN3KG34BRkb7xV1P/YN.qZpBv.WsLXddKPQ4tufO7GO/Nt1Q5LS', 'admin');

-- System settings including sensitive configuration
INSERT INTO system_settings (setting_key, setting_value) VALUES
('app_name', 'Open WebUI'),
('app_version', '0.3.8'),
('allow_signup', 'true'),
('default_model', 'llama3.1:latest'),
('webhook_url', ''),
('admin_secret_note', '@FLAG@'),
('telemetry_enabled', 'true'),
('jwt_expiry', '86400');

-- Default models
INSERT INTO models (name, base_model, description, is_active) VALUES
('Llama 3.1', 'llama3.1:latest', 'Meta Llama 3.1 - 8B parameter model', 1),
('Mistral', 'mistral:latest', 'Mistral 7B Instruct', 1),
('CodeLlama', 'codellama:latest', 'Code Llama - optimized for code generation', 0);

-- Some default chat messages
INSERT INTO chat_messages (user_id, channel, content) VALUES
(1, 'general', 'Welcome to Open WebUI! This is the general chat channel.'),
(1, 'general', 'Please follow the community guidelines when posting messages.');
