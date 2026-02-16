CREATE DATABASE IF NOT EXISTS wikiengine;
CREATE USER IF NOT EXISTS 'wikiapp'@'%' IDENTIFIED BY 'Kj7#mP9xR2vL';

USE wikiengine;

-- Core wiki documents table
DROP TABLE IF EXISTS wiki_documents;
CREATE TABLE wiki_documents (
    doc_id INT PRIMARY KEY AUTO_INCREMENT,
    doc_fullname VARCHAR(255) NOT NULL,
    doc_title VARCHAR(255) NOT NULL,
    doc_space VARCHAR(128) NOT NULL DEFAULT 'Main',
    doc_language VARCHAR(10) NOT NULL DEFAULT 'en',
    doc_hidden TINYINT(1) NOT NULL DEFAULT 0,
    doc_content TEXT,
    doc_author VARCHAR(128),
    doc_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    doc_modified DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Wiki spaces/namespaces
DROP TABLE IF EXISTS wiki_spaces;
CREATE TABLE wiki_spaces (
    space_id INT PRIMARY KEY AUTO_INCREMENT,
    space_name VARCHAR(128) NOT NULL UNIQUE,
    space_description TEXT,
    space_hidden TINYINT(1) NOT NULL DEFAULT 0
);

-- Users and authentication
DROP TABLE IF EXISTS wiki_users;
CREATE TABLE wiki_users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(128) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    user_role VARCHAR(64) NOT NULL DEFAULT 'viewer',
    active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Site configuration and properties
DROP TABLE IF EXISTS site_properties;
CREATE TABLE site_properties (
    prop_id INT PRIMARY KEY AUTO_INCREMENT,
    prop_name VARCHAR(255) NOT NULL,
    prop_value TEXT NOT NULL,
    prop_category VARCHAR(128) DEFAULT 'general'
);

-- Audit log
DROP TABLE IF EXISTS wiki_audit_log;
CREATE TABLE wiki_audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    log_action VARCHAR(64) NOT NULL,
    log_user VARCHAR(128),
    log_details TEXT,
    log_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed wiki spaces
INSERT INTO wiki_spaces (space_name, space_description) VALUES
('Main', 'Main wiki space'),
('Documentation', 'Project documentation'),
('Internal', 'Internal team pages'),
('Archive', 'Archived content');

-- Seed wiki documents
INSERT INTO wiki_documents (doc_fullname, doc_title, doc_space, doc_language, doc_content, doc_author) VALUES
('Main.Welcome', 'Welcome to WikiEngine', 'Main', 'en', 'Welcome to our collaborative wiki platform. Use the navigation to browse content.', 'admin'),
('Main.GettingStarted', 'Getting Started Guide', 'Main', 'en', 'This guide helps new users get started with WikiEngine. You can create pages, edit content, and collaborate with your team.', 'admin'),
('Documentation.APIReference', 'API Reference', 'Documentation', 'en', 'WikiEngine provides a powerful query API for content retrieval. Authenticated users with editor or admin roles can use the content query endpoint to search across documents.', 'admin'),
('Documentation.QuerySyntax', 'Query Syntax Guide', 'Documentation', 'en', 'The content query API supports short-form queries. Provide a WHERE clause fragment and the system will complete it. Example: where doc_space=''Main'' returns all documents in the Main space.', 'admin'),
('Documentation.UserManagement', 'User Management', 'Documentation', 'en', 'WikiEngine supports multiple user roles: viewer, editor, and admin. Editors can use the content query API. Admins have full system access.', 'admin'),
('Internal.TeamNotes', 'Team Meeting Notes', 'Internal', 'en', 'Weekly standup notes for the development team.', 'editor1'),
('Internal.Roadmap', 'Product Roadmap Q1', 'Internal', 'en', 'Priority items for Q1 release cycle.', 'editor1'),
('Archive.LegacyDocs', 'Legacy Documentation', 'Archive', 'en', 'Archived documentation from previous versions.', 'admin'),
('Documentation.SandboxAccess', 'Sandbox Environment Access', 'Documentation', 'en', 'For evaluation purposes, the following accounts are available on this sandbox instance:\n\n- editor1 / ContentEditor99 (Editor role)\n- viewer1 / ReadOnly2024 (Viewer role)\n\nEditors have access to the Content Query API for advanced document searches. Please do not modify production content.', 'admin');

INSERT INTO wiki_users (username, password_hash, display_name, user_role) VALUES
('admin', '$2y$10$mrtRm2sc238m9t3SF4jlQOFsrB./ijdWpYpPoZqIh82AdLxh/5nym', 'System Administrator', 'admin'),
('editor1', '$2y$10$aZHK9yAnuMJ1wUS/ys6eh.KUy3G2PagO4QW9AotFMQCLMGoLpQdZ.', 'Content Editor', 'editor'),
('viewer1', '$2y$10$d99.L7kFUNMu2Po6bpcabeEqOHEo3hi0DERKVBnURAIKHlgnhQTke', 'Read Only User', 'viewer');

-- Seed site properties
INSERT INTO site_properties (prop_name, prop_value, prop_category) VALUES
('site.title', 'WikiEngine Platform', 'display'),
('site.version', '3.8.2', 'system'),
('site.theme', 'default-blue', 'display'),
('mail.smtp.host', 'mail.internal.local', 'mail'),
('mail.smtp.port', '587', 'mail'),
('auth.session.timeout', '3600', 'security'),
('auth.max.attempts', '5', 'security');

GRANT SELECT, INSERT, UPDATE ON wikiengine.* TO 'wikiapp'@'%';
FLUSH PRIVILEGES;
