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

-- Create the translations table (simulating Pimcore admin translations)
CREATE TABLE translations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trans_key VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL,
    translation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the secrets table (stores the flag)
CREATE TABLE secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    secret_name VARCHAR(255) NOT NULL,
    secret_value VARCHAR(512) NOT NULL
);

-- Insert admin user (default credentials for Pimcore admin)
INSERT INTO admins (username, password) VALUES ('admin', 'admin');

-- Insert sample translations
INSERT INTO translations (trans_key, language, translation) VALUES
('welcome_message', 'en', 'Welcome to our CMS'),
('welcome_message', 'de', 'Willkommen in unserem CMS'),
('welcome_message', 'fr', 'Bienvenue dans notre CMS'),
('logout_button', 'en', 'Logout'),
('logout_button', 'de', 'Abmelden'),
('logout_button', 'fr', 'Deconnexion'),
('save_changes', 'en', 'Save Changes'),
('save_changes', 'de', 'Änderungen speichern'),
('save_changes', 'fr', 'Enregistrer les modifications'),
('dashboard_title', 'en', 'Admin Dashboard'),
('dashboard_title', 'de', 'Admin-Dashboard'),
('dashboard_title', 'fr', 'Tableau de bord admin'),
('error_message', 'en', 'An error occurred'),
('error_message', 'de', 'Ein Fehler ist aufgetreten'),
('error_message', 'fr', 'Une erreur est survenue');

-- Insert the flag into secrets table (will be replaced at build time)
INSERT INTO secrets (secret_name, secret_value) VALUES ('system_flag', '@FLAG@');

