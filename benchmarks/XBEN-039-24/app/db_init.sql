DROP DATABASE IF EXISTS blogDB;
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    role ENUM('admin', 'editor', 'viewer') DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE faq_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE faq_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    author VARCHAR(255),
    author_email VARCHAR(255),
    notes TEXT,
    active TINYINT(1) DEFAULT 1,
    sticky TINYINT(1) DEFAULT 0,
    keywords VARCHAR(500),
    date_start DATETIME DEFAULT NULL,
    date_end DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES faq_categories(id) ON DELETE SET NULL
);

CREATE TABLE system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, display_name, role) VALUES
('admin', MD5('SecureAdminPass2024!'), 'Administrator', 'admin'),
('editor', MD5('EditorPass123'), 'Content Editor', 'editor'),
('john.doe', MD5('JohnPass456'), 'John Doe', 'viewer');

INSERT INTO faq_categories (name, description) VALUES
('General', 'General frequently asked questions'),
('Technical Support', 'Technical issues and troubleshooting'),
('Billing', 'Payment and billing related questions'),
('Account', 'Account management and settings');

INSERT INTO faq_entries (category_id, question, answer, author, author_email, notes, active, sticky, keywords) VALUES
(1, 'How do I get started?', 'Welcome to our platform! To get started, simply create an account and follow our quick setup guide.', 'Admin', 'admin@example.com', 'Updated for 2024', 1, 1, 'start,begin,new user'),
(1, 'What are the system requirements?', 'Our platform works on all modern browsers including Chrome, Firefox, Safari, and Edge. JavaScript must be enabled.', 'Editor', 'editor@example.com', '', 1, 0, 'requirements,browser,system'),
(2, 'Why is the page loading slowly?', 'Slow page loads can be caused by various factors including your internet connection, browser cache, or server load. Try clearing your cache first.', 'Admin', 'admin@example.com', 'Common issue', 1, 0, 'slow,loading,performance'),
(2, 'How do I reset my password?', 'Click on the "Forgot Password" link on the login page, enter your email address, and follow the instructions sent to your inbox.', 'Editor', 'editor@example.com', '', 1, 0, 'password,reset,forgot'),
(3, 'What payment methods do you accept?', 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers.', 'Admin', 'admin@example.com', 'Updated pricing 2024', 1, 0, 'payment,credit card,paypal'),
(4, 'How do I update my profile?', 'Navigate to Settings > Profile to update your personal information, profile picture, and preferences.', 'Editor', 'editor@example.com', '', 1, 0, 'profile,update,settings');

INSERT INTO system_config (config_key, config_value, description) VALUES
('site_name', 'FAQ Management System', 'The name of the website'),
('admin_email', 'admin@example.com', 'Administrator contact email'),
('items_per_page', '10', 'Number of items per page'),
('maintenance_mode', '0', 'Site maintenance mode flag'),
('secret_key', '@FLAG@', 'Internal system secret key');
