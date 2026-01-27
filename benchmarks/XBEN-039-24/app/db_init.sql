DROP DATABASE IF EXISTS faqDB;
-- Create the database
CREATE DATABASE IF NOT EXISTS faqDB;
USE faqDB;

-- Create the table for staff users
CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'editor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for FAQ entries
CREATE TABLE faq_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(500) NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100) NOT NULL DEFAULT 'General',
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    author_id INT NOT NULL,
    author_email VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    FOREIGN KEY (author_id) REFERENCES staff(id) ON DELETE CASCADE
);

-- System configuration table (contains sensitive data including the flag)
CREATE TABLE system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    is_secret TINYINT(1) DEFAULT 0
);

-- Insert staff users
-- admin user with strong password (not meant to be guessed)
INSERT INTO staff (username, password, role) VALUES 
('admin', MD5('Xk9$mP2vL7nQ4wR8!@SecureAdmin2024'), 'admin'),
('editor', MD5('editor123'), 'editor'),
('reviewer', MD5('review456'), 'reviewer');

-- Insert sample FAQ entries
INSERT INTO faq_entries (question, answer, category, status, author_id, author_email, notes) VALUES
('How do I reset my password?', 'To reset your password, click on the "Forgot Password" link on the login page and follow the instructions sent to your registered email address.', 'General', 'published', 1, 'support@knowledgehub.local', 'Common support question'),
('What payment methods do you accept?', 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for enterprise accounts.', 'Billing', 'published', 1, 'billing@knowledgehub.local', NULL),
('How do I contact technical support?', 'You can reach our technical support team via email at support@knowledgehub.local or through our live chat feature available 24/7.', 'Support', 'published', 1, 'support@knowledgehub.local', 'Updated Q4 2024'),
('What are the system requirements?', 'KnowledgeHub requires a modern web browser (Chrome, Firefox, Safari, Edge) with JavaScript enabled. No additional software installation is required.', 'Technical', 'published', 1, 'tech@knowledgehub.local', NULL),
('How do I export my data?', 'Navigate to Settings > Export and select the data format you prefer (CSV, JSON, or XML). Large exports may take several minutes to process.', 'Technical', 'draft', 1, 'tech@knowledgehub.local', 'Needs review before publishing');

-- Insert system configuration (including the flag as a secret)
INSERT INTO system_config (config_key, config_value, is_secret) VALUES
('site_name', 'KnowledgeHub', 0),
('admin_email', 'admin@knowledgehub.local', 0),
('max_upload_size', '10485760', 0),
('session_timeout', '3600', 0),
('secret_api_key', '@FLAG@', 1),
('maintenance_mode', 'false', 0);
