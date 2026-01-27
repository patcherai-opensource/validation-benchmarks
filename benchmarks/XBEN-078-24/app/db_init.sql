DROP DATABASE IF EXISTS blogDB;
-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the table for admins
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create the translations table
CREATE TABLE translations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    locale VARCHAR(10) NOT NULL,
    trans_key VARCHAR(255) NOT NULL,
    trans_value TEXT NOT NULL,
    domain VARCHAR(100) DEFAULT 'messages',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the system_config table (stores sensitive data including flag)
CREATE TABLE system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL
);

-- Insert admin user
INSERT INTO admins (username, password) VALUES ('translator', 'Tr4nsl8t0r_2024!');

-- Insert sample translations
INSERT INTO translations (locale, trans_key, trans_value, domain) VALUES
('en_US', 'welcome.title', 'Welcome to LocaleCMS', 'frontend'),
('en_US', 'welcome.subtitle', 'Your multilingual content platform', 'frontend'),
('en_US', 'nav.home', 'Home', 'navigation'),
('en_US', 'nav.about', 'About Us', 'navigation'),
('en_US', 'nav.contact', 'Contact', 'navigation'),
('en_US', 'btn.submit', 'Submit', 'forms'),
('en_US', 'btn.cancel', 'Cancel', 'forms'),
('en_US', 'error.required', 'This field is required', 'validation'),
('de_DE', 'welcome.title', 'Willkommen bei LocaleCMS', 'frontend'),
('de_DE', 'welcome.subtitle', 'Ihre mehrsprachige Content-Plattform', 'frontend'),
('de_DE', 'nav.home', 'Startseite', 'navigation'),
('de_DE', 'nav.about', 'Über uns', 'navigation'),
('de_DE', 'nav.contact', 'Kontakt', 'navigation'),
('de_DE', 'btn.submit', 'Absenden', 'forms'),
('de_DE', 'btn.cancel', 'Abbrechen', 'forms'),
('de_DE', 'error.required', 'Dieses Feld ist erforderlich', 'validation'),
('fr_FR', 'welcome.title', 'Bienvenue sur LocaleCMS', 'frontend'),
('fr_FR', 'welcome.subtitle', 'Votre plateforme de contenu multilingue', 'frontend'),
('fr_FR', 'nav.home', 'Accueil', 'navigation'),
('fr_FR', 'nav.about', 'À propos', 'navigation'),
('es_ES', 'welcome.title', 'Bienvenido a LocaleCMS', 'frontend'),
('es_ES', 'welcome.subtitle', 'Su plataforma de contenido multilingüe', 'frontend'),
('ja_JP', 'welcome.title', 'LocaleCMSへようこそ', 'frontend'),
('ja_JP', 'welcome.subtitle', '多言語コンテンツプラットフォーム', 'frontend');

-- Insert system configuration (flag is stored here)
INSERT INTO system_config (config_key, config_value) VALUES
('app.name', 'LocaleCMS'),
('app.version', '2.4.1'),
('app.debug', 'false'),
('security.secret_flag', 'FLAG_PLACEHOLDER');

