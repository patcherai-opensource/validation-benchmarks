-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- IP to Country mapping table for geolocation redirect service
CREATE TABLE ip_country_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_range_start VARCHAR(45) NOT NULL,
    ip_range_end VARCHAR(45) NOT NULL,
    country_code VARCHAR(3) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Language preferences table
CREATE TABLE language_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL,
    preferred_language VARCHAR(10) NOT NULL,
    redirect_url VARCHAR(255),
    is_active TINYINT(1) DEFAULT 1
);

-- API configuration settings (some internal/hidden)
CREATE TABLE system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    is_public TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session logs for analytics
CREATE TABLE redirect_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45),
    detected_country VARCHAR(3),
    redirect_target VARCHAR(255),
    user_agent TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert IP ranges for various regions
INSERT INTO ip_country_mapping (ip_range_start, ip_range_end, country_code, country_name, region) VALUES
('1.0.0.0', '1.0.0.255', 'AU', 'Australia', 'Oceania'),
('1.0.1.0', '1.0.3.255', 'CN', 'China', 'Asia'),
('1.0.4.0', '1.0.7.255', 'AU', 'Australia', 'Oceania'),
('1.0.8.0', '1.0.15.255', 'CN', 'China', 'Asia'),
('8.8.8.0', '8.8.8.255', 'US', 'United States', 'North America'),
('8.8.4.0', '8.8.4.255', 'US', 'United States', 'North America'),
('91.108.4.0', '91.108.7.255', 'GB', 'United Kingdom', 'Europe'),
('104.16.0.0', '104.31.255.255', 'US', 'United States', 'North America'),
('172.217.0.0', '172.217.255.255', 'US', 'United States', 'North America'),
('185.199.108.0', '185.199.111.255', 'US', 'United States', 'North America'),
('192.168.0.0', '192.168.255.255', 'PRIV', 'Private Network', 'Internal'),
('10.0.0.0', '10.255.255.255', 'PRIV', 'Private Network', 'Internal'),
('77.88.55.0', '77.88.55.255', 'RU', 'Russia', 'Europe'),
('151.101.0.0', '151.101.255.255', 'US', 'United States', 'North America'),
('203.0.113.0', '203.0.113.255', 'TEST', 'Test Network', 'Documentation');

-- Insert language preferences
INSERT INTO language_preferences (country_code, preferred_language, redirect_url, is_active) VALUES
('US', 'en-US', '/en/', 1),
('GB', 'en-GB', '/en-gb/', 1),
('AU', 'en-AU', '/en-au/', 1),
('CN', 'zh-CN', '/zh/', 1),
('RU', 'ru-RU', '/ru/', 1),
('PRIV', 'en-US', '/en/', 1),
('TEST', 'en-US', '/en/', 0);

-- Insert system configuration (including hidden sensitive data)
INSERT INTO system_config (config_key, config_value, is_public) VALUES
('service_name', 'GeoRedirect Pro', 1),
('api_version', '2.1.4', 1),
('max_requests_per_minute', '100', 1),
('enable_logging', 'true', 1),
('cache_ttl_seconds', '3600', 1),
('default_language', 'en-US', 1),
('admin_email', 'admin@georedirect.local', 0),
('license_key', 'GRP-2024-ENTERPRISE-VALID', 0),
('internal_api_secret', '@FLAG@', 0),
('debug_mode', 'false', 0),
('database_backup_path', '/var/backups/georedirect/', 0);

-- Add sample redirect logs
INSERT INTO redirect_logs (ip_address, detected_country, redirect_target, user_agent) VALUES
('8.8.8.8', 'US', '/en/', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
('77.88.55.1', 'RU', '/ru/', 'Mozilla/5.0 (X11; Linux x86_64)'),
('1.0.0.5', 'AU', '/en-au/', 'Mozilla/5.0 (Macintosh; Intel Mac OS X)');
