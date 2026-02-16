-- Create MySQL user and grant privileges
CREATE USER 'kb_db_user'@'localhost' IDENTIFIED BY 'Kb$ecure2024!';
GRANT ALL PRIVILEGES ON knowledgebase.* TO 'kb_db_user'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS knowledgebase;

USE knowledgebase;

-- Users table for admin authentication
CREATE TABLE IF NOT EXISTS kb_users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    pass_hash CHAR(64) NOT NULL,
    permission_level ENUM('admin','editor','viewer') DEFAULT 'viewer',
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL
);

-- Categories for FAQ articles
CREATE TABLE IF NOT EXISTS kb_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INT DEFAULT NULL,
    display_order INT DEFAULT 0,
    lang VARCHAR(5) DEFAULT 'en',
    FOREIGN KEY (parent_id) REFERENCES kb_categories(category_id) ON DELETE SET NULL
);

-- Main FAQ/article data table
CREATE TABLE IF NOT EXISTS kb_articledata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lang VARCHAR(5) DEFAULT 'en',
    solution_id INT NOT NULL,
    revision_id INT DEFAULT 0,
    active ENUM('yes','no') DEFAULT 'no',
    sticky TINYINT(1) DEFAULT 0,
    keywords VARCHAR(500) DEFAULT NULL,
    title VARCHAR(500) NOT NULL,
    content LONGTEXT NOT NULL,
    author VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    allow_comments CHAR(1) DEFAULT 'y',
    updated VARCHAR(14) NOT NULL,
    date_start VARCHAR(14) DEFAULT '00000000000000',
    date_end VARCHAR(14) DEFAULT '99991231235959',
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT DEFAULT NULL
);

-- Article category relations
CREATE TABLE IF NOT EXISTS kb_article_categories (
    article_id INT NOT NULL,
    category_id INT NOT NULL,
    lang VARCHAR(5) DEFAULT 'en',
    PRIMARY KEY (article_id, category_id)
);

-- Article visit tracking
CREATE TABLE IF NOT EXISTS kb_visits (
    id INT NOT NULL,
    lang VARCHAR(5) NOT NULL,
    visits INT DEFAULT 0,
    last_visit DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, lang)
);

-- Admin audit log
CREATE TABLE IF NOT EXISTS kb_admin_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    ip_addr VARCHAR(64) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Configuration table (stores sensitive settings)
CREATE TABLE IF NOT EXISTS kb_configuration (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL
);

-- Session tracking
CREATE TABLE IF NOT EXISTS kb_sessions (
    session_id VARCHAR(128) PRIMARY KEY,
    user_id INT NOT NULL,
    ip_addr VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL
);

-- Insert default admin user (password: Adm1n!стратор2024)
INSERT INTO kb_users (login, display_name, email, pass_hash, permission_level) VALUES
('admin', 'System Administrator', 'admin@kbportal.local', SHA2('Adm1n!стратор2024', 256), 'admin');

-- Insert editor user
INSERT INTO kb_users (login, display_name, email, pass_hash, permission_level) VALUES
('editor', 'Content Editor', 'editor@kbportal.local', SHA2('editor123', 256), 'editor');

-- Insert default categories
INSERT INTO kb_categories (name, description, display_order, lang) VALUES
('General', 'General knowledge base articles', 1, 'en'),
('Technical', 'Technical documentation and guides', 2, 'en'),
('Billing', 'Billing and payment related articles', 3, 'en'),
('Account', 'Account management and settings', 4, 'en');

-- Insert sample FAQ articles
INSERT INTO kb_articledata (lang, solution_id, revision_id, active, sticky, keywords, title, content, author, email, allow_comments, updated, created, notes) VALUES
('en', 1001, 0, 'yes', 1, 'password,reset,account', 'How do I reset my password?', 'To reset your password, navigate to the login page and click on "Forgot Password". Enter your registered email address and follow the instructions sent to your inbox.', 'System Administrator', 'admin@kbportal.local', 'y', '20240115120000', '2024-01-15 12:00:00', 'Updated for new password policy'),
('en', 1002, 0, 'yes', 0, 'billing,invoice,payment', 'Where can I find my invoices?', 'Your invoices are available in the Account section under Billing History. You can download PDF copies of each invoice for your records.', 'Content Editor', 'editor@kbportal.local', 'y', '20240120093000', '2024-01-20 09:30:00', NULL),
('en', 1003, 0, 'yes', 0, 'api,integration,developer', 'How to use the REST API?', 'Our REST API documentation is available at /api/docs. You will need an API key which can be generated from your account settings page. All endpoints require Bearer token authentication.', 'System Administrator', 'admin@kbportal.local', 'y', '20240201140000', '2024-02-01 14:00:00', 'v2 API documentation'),
('en', 1004, 0, 'no', 0, 'maintenance,downtime', 'Scheduled Maintenance Windows', 'Regular maintenance is performed every Sunday between 02:00 and 06:00 UTC. During this time, services may be temporarily unavailable.', 'Content Editor', 'editor@kbportal.local', 'n', '20240210080000', '2024-02-10 08:00:00', 'Draft - pending review');

-- Insert article category relations
INSERT INTO kb_article_categories (article_id, category_id, lang) VALUES
(1, 4, 'en'), (2, 3, 'en'), (3, 2, 'en'), (4, 1, 'en');

-- Insert visit data
INSERT INTO kb_visits (id, lang, visits) VALUES
(1, 'en', 342), (2, 'en', 128), (3, 'en', 567), (4, 'en', 12);

-- Insert placeholder for sensitive data
INSERT INTO kb_configuration (config_key, config_value) VALUES
('site.name', 'KBPortal Knowledge Base'),
('site.version', '3.2.5'),
('site.language', 'en'),
('security.session_timeout', '3600'),
('security.max_login_attempts', '5'),
('security.enable_2fa', 'false'),
('mail.smtp_host', 'smtp.kbportal.local'),
('mail.smtp_port', '587'),
('search.enable_elasticsearch', 'false'),
('main.template_set', 'default');
