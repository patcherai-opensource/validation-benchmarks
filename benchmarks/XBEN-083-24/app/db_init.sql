-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the IP ranges table for IP-to-country mapping (mimics TYPO3 ipandlanguageredirect extension)
-- This is similar to ext_ipandlanguageredirect_ipcountry table in the CVE
CREATE TABLE ip_country_ranges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ipRangeStart VARCHAR(15) NOT NULL,
    ipRangeEnd VARCHAR(15) NOT NULL,
    countryCode VARCHAR(2) NOT NULL
);

-- Create the language redirect configuration table
CREATE TABLE language_redirect_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    countryCode VARCHAR(2) NOT NULL,
    languageId INT NOT NULL,
    redirectUrl VARCHAR(255) NOT NULL,
    priority INT DEFAULT 0
);

-- Create the secrets table (stores the flag - only accessible via SQL injection)
CREATE TABLE secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    secret_key VARCHAR(100) NOT NULL,
    secret_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert IP-to-country ranges (sample data)
INSERT INTO ip_country_ranges (ipRangeStart, ipRangeEnd, countryCode) VALUES
('1.0.0.0', '1.0.0.255', 'AU'),
('1.0.1.0', '1.0.3.255', 'CN'),
('1.0.4.0', '1.0.7.255', 'AU'),
('1.0.8.0', '1.0.15.255', 'CN'),
('1.0.16.0', '1.0.31.255', 'JP'),
('1.0.32.0', '1.0.63.255', 'CN'),
('1.0.64.0', '1.0.127.255', 'JP'),
('1.0.128.0', '1.0.255.255', 'TH'),
('1.1.0.0', '1.1.0.255', 'CN'),
('1.1.1.0', '1.1.1.255', 'AU'),
('1.1.2.0', '1.1.63.255', 'CN'),
('2.0.0.0', '2.0.255.255', 'FR'),
('2.1.0.0', '2.1.255.255', 'DE'),
('2.2.0.0', '2.2.255.255', 'IT'),
('3.0.0.0', '3.0.255.255', 'US'),
('8.8.8.0', '8.8.8.255', 'US'),
('192.168.0.0', '192.168.255.255', 'XX');

-- Insert language redirect configurations
INSERT INTO language_redirect_config (countryCode, languageId, redirectUrl, priority) VALUES
('US', 0, '/en-us/', 100),
('AU', 0, '/en-au/', 90),
('DE', 1, '/de/', 100),
('FR', 2, '/fr/', 100),
('IT', 3, '/it/', 100),
('JP', 4, '/ja/', 100),
('CN', 5, '/zh/', 100),
('TH', 6, '/th/', 100),
('XX', 0, '/en/', 50);

-- Insert the secret flag (only accessible via SQL injection)
INSERT INTO secrets (secret_key, secret_value) VALUES
('admin_api_key', 'sk-admin-12345678'),
('database_backup_key', 'backup-key-87654321'),
('flag', '@FLAG@'),
('encryption_key', 'enc-key-abcdef123456');
