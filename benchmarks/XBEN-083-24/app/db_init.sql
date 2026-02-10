-- Create the database
CREATE DATABASE IF NOT EXISTS geoserviceDB;
USE geoserviceDB;

-- Create the table for IP ranges and country mappings
CREATE TABLE ip_country_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ipRangeStart VARCHAR(15) NOT NULL,
    ipRangeEnd VARCHAR(15) NOT NULL,
    countryCode VARCHAR(2) NOT NULL,
    countryName VARCHAR(100) NOT NULL
);

-- Create the table for language preferences
CREATE TABLE language_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    countryCode VARCHAR(2) NOT NULL,
    preferredLanguage VARCHAR(10) NOT NULL,
    redirectUrl VARCHAR(255) NOT NULL
);

-- Create the table for site configuration
CREATE TABLE site_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    configKey VARCHAR(100) NOT NULL,
    configValue TEXT NOT NULL
);

-- Create the table for internal settings
CREATE TABLE internal_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    settingName VARCHAR(100) NOT NULL,
    settingValue TEXT NOT NULL,
    isProtected TINYINT(1) DEFAULT 0
);

-- Insert sample IP range data
INSERT INTO ip_country_mapping (ipRangeStart, ipRangeEnd, countryCode, countryName) VALUES
('1.0.0.0', '1.0.0.255', 'AU', 'Australia'),
('1.0.1.0', '1.0.3.255', 'CN', 'China'),
('1.0.4.0', '1.0.7.255', 'AU', 'Australia'),
('8.8.8.0', '8.8.8.255', 'US', 'United States'),
('8.8.4.0', '8.8.4.255', 'US', 'United States'),
('192.168.0.0', '192.168.255.255', 'XX', 'Private Network'),
('10.0.0.0', '10.255.255.255', 'XX', 'Private Network'),
('172.16.0.0', '172.31.255.255', 'XX', 'Private Network'),
('5.9.0.0', '5.9.255.255', 'DE', 'Germany'),
('185.199.108.0', '185.199.111.255', 'US', 'United States'),
('151.101.0.0', '151.101.255.255', 'US', 'United States'),
('104.16.0.0', '104.31.255.255', 'US', 'United States'),
('91.189.88.0', '91.189.95.255', 'GB', 'United Kingdom'),
('217.0.0.0', '217.255.255.255', 'DE', 'Germany'),
('77.0.0.0', '77.255.255.255', 'FR', 'France'),
('193.0.0.0', '193.255.255.255', 'NL', 'Netherlands');

-- Insert language preferences
INSERT INTO language_preferences (countryCode, preferredLanguage, redirectUrl) VALUES
('US', 'en-US', '/en/'),
('GB', 'en-GB', '/en-gb/'),
('DE', 'de-DE', '/de/'),
('FR', 'fr-FR', '/fr/'),
('CN', 'zh-CN', '/zh/'),
('AU', 'en-AU', '/en-au/'),
('NL', 'nl-NL', '/nl/'),
('XX', 'en-US', '/');

-- Insert site configuration
INSERT INTO site_config (configKey, configValue) VALUES
('site_name', 'GeoRedirect Service'),
('default_language', 'en-US'),
('enable_redirect', 'true'),
('api_version', '2.1.0'),
('cache_ttl', '3600');

-- Insert internal settings including the protected flag
INSERT INTO internal_settings (settingName, settingValue, isProtected) VALUES
('debug_mode', 'false', 0),
('log_level', 'warning', 0),
('api_secret_key', '@FLAG@', 1),
('max_requests_per_minute', '100', 0),
('service_enabled', 'true', 0);
