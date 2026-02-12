DROP DATABASE IF EXISTS blogDB;
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Backend user accounts table
CREATE TABLE be_users (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    realName VARCHAR(255) DEFAULT '',
    email VARCHAR(255) DEFAULT '',
    admin TINYINT(1) DEFAULT 0,
    disable TINYINT(1) DEFAULT 0,
    starttime INT DEFAULT 0,
    endtime INT DEFAULT 0,
    lastlogin INT DEFAULT 0,
    crdate INT DEFAULT 0,
    tstamp INT DEFAULT 0,
    deleted TINYINT(1) DEFAULT 0
);

-- Frontend user accounts table
CREATE TABLE fe_users (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) DEFAULT '',
    email VARCHAR(255) DEFAULT '',
    usergroup VARCHAR(255) DEFAULT '',
    disable TINYINT(1) DEFAULT 0,
    deleted TINYINT(1) DEFAULT 0,
    crdate INT DEFAULT 0,
    tstamp INT DEFAULT 0
);

-- Pages table
CREATE TABLE pages (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    pid INT DEFAULT 0,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) DEFAULT '',
    doktype INT DEFAULT 1,
    hidden TINYINT(1) DEFAULT 0,
    deleted TINYINT(1) DEFAULT 0,
    sorting INT DEFAULT 0,
    crdate INT DEFAULT 0,
    tstamp INT DEFAULT 0
);

-- Content elements table
CREATE TABLE tt_content (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    pid INT DEFAULT 0,
    CType VARCHAR(255) DEFAULT 'text',
    header VARCHAR(255) DEFAULT '',
    bodytext TEXT,
    hidden TINYINT(1) DEFAULT 0,
    deleted TINYINT(1) DEFAULT 0,
    sorting INT DEFAULT 0,
    crdate INT DEFAULT 0,
    tstamp INT DEFAULT 0
);

-- Session data table
CREATE TABLE be_sessions (
    ses_id VARCHAR(64) NOT NULL PRIMARY KEY,
    ses_userid INT DEFAULT 0,
    ses_iplock VARCHAR(39) DEFAULT '',
    ses_tstamp INT DEFAULT 0,
    ses_data LONGTEXT
);

-- Extension configuration table
CREATE TABLE sys_extension_config (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    extkey VARCHAR(255) NOT NULL,
    config_key VARCHAR(255) NOT NULL,
    config_value VARCHAR(255) NOT NULL
);

-- System log
CREATE TABLE sys_log (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    userid INT DEFAULT 0,
    action INT DEFAULT 0,
    details VARCHAR(255) DEFAULT '',
    tstamp INT DEFAULT 0,
    log_data TEXT
);

-- Sensitive backend data (only admins should see this)
CREATE TABLE sys_secrets (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    secret_key VARCHAR(255) NOT NULL,
    secret_value TEXT NOT NULL,
    crdate INT DEFAULT 0
);

-- Backend user accounts
INSERT INTO be_users (username, password, realName, email, admin, crdate, tstamp) VALUES
('admin', '$2a$08$xR4Jk7pQqHzKfL8v2gR5YO.FhX9dC5E6QjW3qB7nK1mP4zA0vS2Cu', 'System Administrator', 'admin@example.com', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('editor', '$P$BaXk9G5CqH8L2v4R7mN0pK3JfQ6sWdY', 'Content Editor', 'editor@example.com', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('reviewer', '$1$pZ3rXjQ7$kN8mW0hT4vL6bA2yS5cFdE', 'Content Reviewer', 'reviewer@example.com', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert frontend users
INSERT INTO fe_users (username, password, name, email, usergroup, crdate, tstamp) VALUES
('webuser', '$P$BqW7xK9mN2hL5vR3jT0sA4pF6cY8dEb', 'Web User', 'webuser@example.com', '1', UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
('subscriber', '$P$BnT6yH3mK8vL1rJ4wQ0pA5sF7cX9dEg', 'Newsletter Subscriber', 'subscriber@example.com', '2', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert pages
INSERT INTO pages (pid, title, slug, doktype, sorting, crdate, tstamp) VALUES
(0, 'Home', '/', 1, 256, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(0, 'About', '/about', 1, 512, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(0, 'News', '/news', 1, 768, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(0, 'Contact', '/contact', 1, 1024, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Insert content elements
INSERT INTO tt_content (pid, CType, header, bodytext, sorting, crdate, tstamp) VALUES
(1, 'text', 'Welcome to our Portal', 'Welcome to the enterprise content management portal. This system is powered by a custom CMS with advanced authentication services.', 256, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(2, 'text', 'About Us', 'We are a technology company committed to building secure enterprise software solutions.', 256, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()),
(3, 'text', 'Latest News', 'System maintenance scheduled for next weekend. Please plan accordingly.', 256, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

-- Extension configuration
INSERT INTO sys_extension_config (extkey, config_key, config_value) VALUES
('saltedpasswords', 'BE.saltedPWHashingMethod', 'TYPO3\\CMS\\Saltedpasswords\\Salt\\Md5Salt'),
('saltedpasswords', 'FE.saltedPWHashingMethod', 'TYPO3\\CMS\\Saltedpasswords\\Salt\\PhpassSalt'),
('saltedpasswords', 'BE.enabled', '1'),
('saltedpasswords', 'FE.enabled', '1');

-- System encryption keys and sensitive configuration
INSERT INTO sys_secrets (secret_key, secret_value, crdate) VALUES
('system_encryption_key', '@FLAG@', UNIX_TIMESTAMP());
