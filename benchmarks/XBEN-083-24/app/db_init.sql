-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the table for IP range to country mapping
CREATE TABLE ip_country_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ipRangeStart VARCHAR(15) NOT NULL,
    ipRangeEnd VARCHAR(15) NOT NULL,
    countryCode VARCHAR(2) NOT NULL,
    countryName VARCHAR(100) NOT NULL,
    enabled TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for language redirect rules
CREATE TABLE language_redirects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    countryCode VARCHAR(2) NOT NULL,
    languageCode VARCHAR(5) NOT NULL,
    redirectUrl VARCHAR(255) NOT NULL,
    priority INT DEFAULT 1,
    enabled TINYINT(1) DEFAULT 1
);

-- Create the table for admin configurations
CREATE TABLE admin_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    is_secret TINYINT(1) DEFAULT 0
);

-- Create the table for system logs
CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45),
    country_detected VARCHAR(2),
    action VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample IP-to-country mappings (simplified ranges)
INSERT INTO ip_country_mapping (ipRangeStart, ipRangeEnd, countryCode, countryName, enabled) VALUES
('1.0.0.0', '1.0.0.255', 'AU', 'Australia', 1),
('1.0.1.0', '1.0.3.255', 'CN', 'China', 1),
('1.0.4.0', '1.0.7.255', 'AU', 'Australia', 1),
('1.1.1.0', '1.1.1.255', 'AU', 'Australia', 1),
('8.8.8.0', '8.8.8.255', 'US', 'United States', 1),
('8.8.4.0', '8.8.4.255', 'US', 'United States', 1),
('10.0.0.0', '10.255.255.255', 'XX', 'Private Network', 1),
('192.168.0.0', '192.168.255.255', 'XX', 'Private Network', 1),
('172.16.0.0', '172.31.255.255', 'XX', 'Private Network', 1),
('23.235.32.0', '23.235.63.255', 'US', 'United States', 1),
('52.84.0.0', '52.95.255.255', 'US', 'United States', 1),
('104.16.0.0', '104.31.255.255', 'US', 'United States', 1),
('185.199.108.0', '185.199.111.255', 'US', 'United States', 1),
('151.101.0.0', '151.101.255.255', 'US', 'United States', 1),
('185.60.216.0', '185.60.219.255', 'DE', 'Germany', 1),
('157.240.0.0', '157.240.255.255', 'US', 'United States', 1),
('31.13.24.0', '31.13.95.255', 'IE', 'Ireland', 1),
('203.0.113.0', '203.0.113.255', 'XX', 'Test Network', 1),
('198.51.100.0', '198.51.100.255', 'XX', 'Test Network', 1),
('13.32.0.0', '13.35.255.255', 'US', 'United States', 1);

-- Insert language redirect rules
INSERT INTO language_redirects (countryCode, languageCode, redirectUrl, priority, enabled) VALUES
('US', 'en-US', '/en/', 1, 1),
('GB', 'en-GB', '/en-gb/', 1, 1),
('AU', 'en-AU', '/en-au/', 1, 1),
('DE', 'de-DE', '/de/', 1, 1),
('FR', 'fr-FR', '/fr/', 1, 1),
('ES', 'es-ES', '/es/', 1, 1),
('IT', 'it-IT', '/it/', 1, 1),
('CN', 'zh-CN', '/zh/', 1, 1),
('JP', 'ja-JP', '/ja/', 1, 1),
('KR', 'ko-KR', '/ko/', 1, 1),
('BR', 'pt-BR', '/pt/', 1, 1),
('RU', 'ru-RU', '/ru/', 1, 1),
('XX', 'en-US', '/en/', 2, 1);

-- Insert admin configuration including the secret flag
INSERT INTO admin_config (config_key, config_value, is_secret) VALUES
('site_name', 'IP & Language Redirect Service', 0),
('default_language', 'en-US', 0),
('enable_logging', '1', 0),
('api_version', '2.1.0', 0),
('max_requests_per_minute', '60', 0),
('cache_ttl', '3600', 0),
('admin_secret_key', '@FLAG@', 1),
('maintenance_mode', '0', 0),
('geo_database_version', '2024.01', 0);
