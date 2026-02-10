-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the table for datasources
CREATE TABLE datasources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    db_type VARCHAR(50) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INT DEFAULT 3306,
    username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for queries history
CREATE TABLE query_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    datasource_id INT,
    query_text TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INT DEFAULT 0,
    FOREIGN KEY (datasource_id) REFERENCES datasources(id) ON DELETE CASCADE
);

-- Create the table for users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for system configurations
CREATE TABLE system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for internal secrets
CREATE TABLE internal_secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    secret_name VARCHAR(255) NOT NULL,
    secret_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample datasources
INSERT INTO datasources (name, db_type, host, port, username) VALUES
('Production MySQL', 'mysql', 'prod-db.internal', 3306, 'app_user'),
('Analytics Postgres', 'postgresql', 'analytics.internal', 5432, 'analytics_ro'),
('Development SQLite', 'sqlite', 'localhost', 0, 'dev_user');

-- Insert sample query history
INSERT INTO query_history (datasource_id, query_text, execution_time_ms) VALUES
(1, 'SELECT COUNT(*) FROM users', 45),
(1, 'SELECT * FROM orders WHERE status = ''pending''', 120),
(2, 'SELECT date, SUM(revenue) FROM sales GROUP BY date', 350);

-- Insert sample users
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@dbgpt.local', '$2y$10$abcdefghijklmnopqrstuv', 'admin'),
('analyst', 'analyst@dbgpt.local', '$2y$10$wxyzabcdefghijklmnopqr', 'user'),
('developer', 'dev@dbgpt.local', '$2y$10$123456789abcdefghijklm', 'user');

-- Insert system configurations
INSERT INTO system_config (config_key, config_value) VALUES
('max_query_timeout', '30'),
('default_result_limit', '1000'),
('enable_query_logging', 'true'),
('api_rate_limit', '100');

-- Insert internal secret (flag)
INSERT INTO internal_secrets (secret_name, secret_value) VALUES
('api_master_key', '@FLAG@');
