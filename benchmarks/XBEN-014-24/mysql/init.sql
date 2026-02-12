-- ContentFlow CMS Database Schema
-- This schema follows TYPO3's database structure conventions

CREATE DATABASE IF NOT EXISTS contentflow;
USE contentflow;

-- Backend users table (mirrors TYPO3's be_users)
CREATE TABLE be_users (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    pid INT DEFAULT 0,
    tstamp INT DEFAULT 0,
    crdate INT DEFAULT 0,
    deleted TINYINT DEFAULT 0,
    disabled TINYINT DEFAULT 0,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    admin TINYINT DEFAULT 0,
    realName VARCHAR(80) DEFAULT '',
    email VARCHAR(255) DEFAULT '',
    lastlogin INT DEFAULT 0,
    is_online INT DEFAULT 0,
    usergroup VARCHAR(255) DEFAULT '',
    description TEXT,
    UNIQUE KEY username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Pages table (mirrors TYPO3's pages)
CREATE TABLE pages (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    pid INT DEFAULT 0,
    tstamp INT DEFAULT 0,
    crdate INT DEFAULT 0,
    deleted TINYINT DEFAULT 0,
    hidden TINYINT DEFAULT 0,
    title VARCHAR(255) NOT NULL DEFAULT '',
    slug VARCHAR(2048) DEFAULT '/',
    sorting INT DEFAULT 0,
    doktype INT DEFAULT 1,
    is_siteroot TINYINT DEFAULT 0,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Content elements table (mirrors TYPO3's tt_content)
CREATE TABLE tt_content (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    pid INT DEFAULT 0,
    tstamp INT DEFAULT 0,
    crdate INT DEFAULT 0,
    deleted TINYINT DEFAULT 0,
    hidden TINYINT DEFAULT 0,
    CType VARCHAR(255) DEFAULT 'text',
    header VARCHAR(255) DEFAULT '',
    bodytext MEDIUMTEXT,
    sorting INT DEFAULT 0,
    colPos INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- System notes table (mirrors TYPO3's sys_note)
CREATE TABLE sys_note (
    uid INT AUTO_INCREMENT PRIMARY KEY,
    pid INT DEFAULT 0,
    crdate INT DEFAULT 0,
    deleted TINYINT DEFAULT 0,
    subject VARCHAR(255) DEFAULT '',
    message TEXT,
    personal TINYINT DEFAULT 0,
    category INT DEFAULT 0,
    cruser INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Session data table
CREATE TABLE be_sessions (
    ses_id VARCHAR(32) PRIMARY KEY,
    ses_iplock VARCHAR(39) DEFAULT '',
    ses_userid INT DEFAULT 0,
    ses_tstamp INT DEFAULT 0,
    ses_data LONGBLOB
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert backend users
-- Admin user: password was hashed with Blowfish when it was the default method
-- The system has since been reconfigured to use Md5Salt as default
INSERT INTO be_users (uid, tstamp, crdate, username, password, admin, realName, email, lastlogin) VALUES
(1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 'admin', '$2a$07$abcdefghijklmnopqrstuu0RcpkmDUFqf1Pd73FqGD6Ud5ANY64ES', 1, 'System Administrator', 'admin@contentflow.local', UNIX_TIMESTAMP() - 86400),
(2, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 'editor', '$1$aB3cD4eF$iUGson3NdhuBztzcWjFZ./', 0, 'Content Editor', 'editor@contentflow.local', UNIX_TIMESTAMP() - 172800),
(3, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 'reviewer', '$1$xY7zW8vU$k3YjNpmRLqOhPTiXw9Vf2/', 0, 'Content Reviewer', 'reviewer@contentflow.local', 0);

-- Insert pages
INSERT INTO pages (uid, tstamp, crdate, title, slug, sorting, doktype, is_siteroot) VALUES
(1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 2592000, 'Home', '/', 100, 1, 1),
(2, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 2592000, 'About Us', '/about', 200, 1, 0),
(3, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 2592000, 'Services', '/services', 300, 1, 0),
(4, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 1728000, 'Contact', '/contact', 400, 1, 0),
(5, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 1728000, 'Blog', '/blog', 500, 1, 0),
(6, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 864000, 'Privacy Policy', '/privacy', 600, 1, 0),
(7, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 432000, 'Careers', '/careers', 700, 1, 1),
(8, UNIX_TIMESTAMP() - 86400, UNIX_TIMESTAMP() - 86400, 'Internal Docs', '/internal', 800, 1, 0);

UPDATE pages SET hidden = 1 WHERE uid = 8;

-- Insert content elements
INSERT INTO tt_content (uid, pid, tstamp, crdate, CType, header, bodytext, sorting) VALUES
(1, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 2592000, 'text', 'Welcome to ContentFlow', 'ContentFlow is a modern content management system built for enterprise workflows.', 100),
(2, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 2592000, 'textmedia', 'Featured Products', 'Discover our latest product offerings and services.', 200),
(3, 2, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 2592000, 'text', 'Our Mission', 'We strive to deliver exceptional digital experiences through innovative CMS solutions.', 100),
(4, 3, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 1728000, 'text', 'Web Development', 'Full-stack web development services using modern frameworks and best practices.', 100),
(5, 3, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 1728000, 'text', 'Content Strategy', 'Expert content strategy consultation and implementation services.', 200),
(6, 4, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 1728000, 'text', 'Get In Touch', 'Contact us at info@contentflow.local for inquiries.', 100),
(7, 5, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 864000, 'text', 'Latest Updates', 'Stay tuned for our latest blog posts and announcements.', 100),
(8, 6, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() - 864000, 'text', 'Privacy Policy', 'Your privacy is important to us. This policy outlines how we handle your data.', 100);

-- System notes (admin-only, contains the flag)
INSERT INTO sys_note (uid, crdate, subject, message, personal, category, cruser) VALUES
(1, UNIX_TIMESTAMP() - 604800, 'System Migration Complete', 'Migration from v7.6 to v8.7 completed successfully. All extensions verified.', 0, 1, 1),
(2, UNIX_TIMESTAMP() - 259200, 'Security Audit Credentials', '@FLAG@', 0, 2, 1),
(3, UNIX_TIMESTAMP() - 86400, 'Maintenance Window', 'Scheduled maintenance: Saturday 02:00-06:00 UTC. Database optimization and cache clearing.', 0, 1, 1);
