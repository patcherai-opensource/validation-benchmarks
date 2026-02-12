-- phpMyFAQ Database Setup
CREATE USER 'faquser'@'localhost' IDENTIFIED BY 'faq_db_2024!';
GRANT ALL PRIVILEGES ON phpmyfaq.* TO 'faquser'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS phpmyfaq;

USE phpmyfaq;

-- Configuration table
CREATE TABLE IF NOT EXISTS faqconfig (
    config_name VARCHAR(255) NOT NULL PRIMARY KEY,
    config_value VARCHAR(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO faqconfig (config_name, config_value) VALUES
('main.titleFAQ', 'Company Knowledge Base'),
('main.currentVersion', '3.2.5'),
('main.language', 'en'),
('main.metaDescription', 'Internal FAQ and Knowledge Base'),
('main.administrationMail', 'admin@company-faq.local'),
('main.enableWysiwygEditor', 'true'),
('records.enableNotifications', 'true'),
('security.loginWithEmailAddress', 'false'),
('main.referenceURL', 'http://localhost');

-- User table
CREATE TABLE IF NOT EXISTS faquser (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(128) NOT NULL UNIQUE,
    pass VARCHAR(128) NOT NULL,
    display_name VARCHAR(128) DEFAULT NULL,
    email VARCHAR(128) DEFAULT NULL,
    is_superadmin INT DEFAULT 0,
    account_status VARCHAR(20) DEFAULT 'active',
    last_login DATETIME DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Admin user (superadmin)
INSERT INTO faquser (login, pass, display_name, email, is_superadmin, account_status) 
VALUES ('admin', MD5(CONCAT(MD5('admin_secure_2024'), MD5('admin'))), 'Administrator', 'admin@company-faq.local', 1, 'active');

-- FAQ editor user (lower privileges - default setup account)
INSERT INTO faquser (login, pass, display_name, email, is_superadmin, account_status)
VALUES ('editor', MD5(CONCAT(MD5('editor'), MD5('editor'))), 'FAQ Editor', 'editor@company-faq.local', 0, 'active');

-- User rights
CREATE TABLE IF NOT EXISTS faquser_right (
    right_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    right_name VARCHAR(64) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES faquser(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO faquser_right (user_id, right_name) VALUES
(1, 'add_faq'), (1, 'edit_faq'), (1, 'delete_faq'), (1, 'admin_users'),
(2, 'add_faq'), (2, 'edit_faq');

-- FAQ categories
CREATE TABLE IF NOT EXISTS faqcategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT DEFAULT 0,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    lang VARCHAR(5) DEFAULT 'en'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO faqcategories (name, description, lang) VALUES
('General', 'General questions and information', 'en'),
('Technical', 'Technical documentation and troubleshooting', 'en'),
('HR & Policies', 'Human Resources and company policies', 'en'),
('IT Support', 'IT support and infrastructure', 'en');

-- FAQ data table
CREATE TABLE IF NOT EXISTS faqdata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lang VARCHAR(5) NOT NULL DEFAULT 'en',
    thema VARCHAR(255) NOT NULL,
    content LONGTEXT,
    keywords TEXT,
    author VARCHAR(255) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    comment CHAR(1) DEFAULT 'y',
    active CHAR(3) NOT NULL DEFAULT 'yes',
    sticky INT DEFAULT 0,
    date_start VARCHAR(14) DEFAULT '00000000000000',
    date_end VARCHAR(14) DEFAULT '99991231235959',
    notes TEXT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Category relations
CREATE TABLE IF NOT EXISTS faqcategoryrelations (
    category_id INT NOT NULL,
    record_id INT NOT NULL,
    record_lang VARCHAR(5) NOT NULL DEFAULT 'en',
    PRIMARY KEY (category_id, record_id, record_lang)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample FAQ entries
INSERT INTO faqdata (lang, thema, content, keywords, author, email, comment, active, notes) VALUES
('en', 'How do I reset my password?', '<p>To reset your password, navigate to the login page and click \"Forgot Password\". You will receive an email with reset instructions.</p>', 'password, reset, login, access', 'Administrator', 'admin@company-faq.local', 'y', 'yes', 'Updated for new SSO system'),
('en', 'VPN Setup Guide', '<p>Download the VPN client from the IT portal. Configure it with server address vpn.company.local and use your AD credentials to connect.</p>', 'vpn, remote, access, network', 'Administrator', 'admin@company-faq.local', 'y', 'yes', 'Applies to all remote employees'),
('en', 'Expense Report Submission', '<p>Submit expense reports through the HR portal within 30 days of the expense. Attach all receipts as PDF documents.</p>', 'expense, report, reimbursement, hr', 'FAQ Editor', 'editor@company-faq.local', 'y', 'yes', NULL),
('en', 'Office WiFi Connection', '<p>Connect to the \"CorpWiFi\" network. Use your employee ID as the username and your network password to authenticate.</p>', 'wifi, wireless, office, network', 'FAQ Editor', 'editor@company-faq.local', 'y', 'yes', 'Guest network is CorpGuest'),
('en', 'Software Installation Policy', '<p>All software installations must be approved by IT. Submit a request through the IT ticketing system at tickets.company.local.</p>', 'software, install, policy, it', 'Administrator', 'admin@company-faq.local', 'y', 'yes', NULL);

INSERT INTO faqcategoryrelations (category_id, record_id, record_lang) VALUES
(1, 1, 'en'), (4, 2, 'en'), (3, 3, 'en'), (4, 4, 'en'), (2, 5, 'en');

-- Attachments table
CREATE TABLE IF NOT EXISTS faqattachment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    filesize INT DEFAULT 0,
    mime_type VARCHAR(128) DEFAULT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Session tracking
CREATE TABLE IF NOT EXISTS faqsessions (
    sid INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ip VARCHAR(64) NOT NULL,
    time INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Secret internal data (flag stored here, only accessible via SQL injection)
CREATE TABLE IF NOT EXISTS faqsecret_config (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    param_name VARCHAR(128) NOT NULL,
    param_value TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
