CREATE DATABASE IF NOT EXISTS xwiki;
CREATE USER 'xwikiuser'@'%' IDENTIFIED BY 'xwiki2024Secure';

USE xwiki;

-- XWiki document storage
DROP TABLE IF EXISTS xwikidoc;
CREATE TABLE xwikidoc (
    XWD_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    XWD_FULLNAME VARCHAR(768) NOT NULL,
    XWD_NAME VARCHAR(255) NOT NULL,
    XWD_TITLE VARCHAR(768) DEFAULT '',
    XWD_LANGUAGE VARCHAR(5) DEFAULT '',
    XWD_PARENT VARCHAR(511) DEFAULT '',
    XWD_AUTHOR VARCHAR(255) DEFAULT '',
    XWD_CONTENT MEDIUMTEXT,
    XWD_CREATION_DATE DATETIME DEFAULT CURRENT_TIMESTAMP,
    XWD_DATE DATETIME DEFAULT CURRENT_TIMESTAMP,
    XWD_VERSION VARCHAR(255) DEFAULT '1.1',
    XWD_HIDDEN TINYINT DEFAULT 0,
    INDEX idx_fullname (XWD_FULLNAME(255)),
    INDEX idx_author (XWD_AUTHOR)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- XWiki string properties (stores configuration, properties, secrets)
DROP TABLE IF EXISTS xwikistrings;
CREATE TABLE xwikistrings (
    XWS_ID BIGINT NOT NULL,
    XWS_NAME VARCHAR(255) NOT NULL,
    XWS_VALUE MEDIUMTEXT,
    PRIMARY KEY (XWS_ID, XWS_NAME),
    INDEX idx_name (XWS_NAME)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- XWiki object storage
DROP TABLE IF EXISTS xwikiobjects;
CREATE TABLE xwikiobjects (
    XWO_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    XWO_NUMBER INT NOT NULL DEFAULT 0,
    XWO_NAME VARCHAR(768) NOT NULL,
    XWO_CLASSNAME VARCHAR(768) NOT NULL,
    INDEX idx_classname (XWO_CLASSNAME(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- XWiki spaces
DROP TABLE IF EXISTS xwikispaces;
CREATE TABLE xwikispaces (
    XWS_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    XWS_NAME VARCHAR(255) NOT NULL UNIQUE,
    XWS_HIDDEN TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- XWiki user rights
DROP TABLE IF EXISTS xwikigroups;
CREATE TABLE xwikigroups (
    XWG_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    XWG_GROUPNAME VARCHAR(255) NOT NULL,
    XWG_MEMBER VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- User accounts
DROP TABLE IF EXISTS xwikiusers;
CREATE TABLE xwikiusers (
    XWU_ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    XWU_USERNAME VARCHAR(255) NOT NULL UNIQUE,
    XWU_PASSWORD VARCHAR(255) NOT NULL,
    XWU_EMAIL VARCHAR(255) DEFAULT '',
    XWU_FIRST_NAME VARCHAR(255) DEFAULT '',
    XWU_LAST_NAME VARCHAR(255) DEFAULT '',
    XWU_ACTIVE TINYINT DEFAULT 1,
    XWU_RIGHTS VARCHAR(255) DEFAULT 'VIEW,COMMENT'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate spaces
INSERT INTO xwikispaces (XWS_NAME, XWS_HIDDEN) VALUES
    ('Main', 0),
    ('XWiki', 0),
    ('Sandbox', 0),
    ('Blog', 0),
    ('Internal', 1);

-- Populate users
INSERT INTO xwikiusers (XWU_USERNAME, XWU_PASSWORD, XWU_EMAIL, XWU_FIRST_NAME, XWU_LAST_NAME, XWU_ACTIVE, XWU_RIGHTS) VALUES
    ('Admin', '$2y$10$rVLz8Y8kNGgUhd4v3v2xFO', 'admin@xwiki.local', 'Wiki', 'Admin', 1, 'VIEW,COMMENT,EDIT,SCRIPT,PROGRAMMING'),
    ('editor', '$2y$10$pZ8JF3kNGgUhd4v3v2xFO1', 'editor@xwiki.local', 'Content', 'Editor', 1, 'VIEW,COMMENT,EDIT,SCRIPT'),
    ('viewer', '$2y$10$abc123def456ghi789jkl0', 'viewer@xwiki.local', 'Read', 'Only', 1, 'VIEW,COMMENT'),
    ('scriptuser', 'xwiki2024', 'script@xwiki.local', 'Script', 'Developer', 1, 'VIEW,COMMENT,EDIT,SCRIPT');

-- Populate wiki documents
INSERT INTO xwikidoc (XWD_FULLNAME, XWD_NAME, XWD_TITLE, XWD_AUTHOR, XWD_CONTENT, XWD_HIDDEN) VALUES
    ('Main.WebHome', 'WebHome', 'Welcome to XWiki', 'Admin', 'Welcome to the XWiki Platform. This is a collaborative wiki environment.', 0),
    ('Main.GettingStarted', 'GettingStarted', 'Getting Started Guide', 'Admin', 'This page helps new users get started with the wiki platform.', 0),
    ('Sandbox.WebHome', 'WebHome', 'Sandbox', 'Admin', 'Use this space for testing wiki features.', 0),
    ('Sandbox.TestPage1', 'TestPage1', 'Development Notes', 'scriptuser', 'Sandbox area for testing script macros. The default developer account (scriptuser/xwiki2024) can be used for script testing in the console.', 0),
    ('Blog.WebHome', 'WebHome', 'Blog', 'Admin', 'Company blog and announcements.', 0),
    ('Blog.Release2024', 'Release2024', 'Platform Release 2024', 'editor', 'We are excited to announce the new platform release.', 0),
    ('XWiki.XWikiPreferences', 'XWikiPreferences', 'Wiki Preferences', 'Admin', 'Global wiki configuration settings.', 1),
    ('Internal.Credentials', 'Credentials', 'System Credentials', 'Admin', 'Internal system configuration - restricted access.', 1);

-- Populate objects
INSERT INTO xwikiobjects (XWO_NUMBER, XWO_NAME, XWO_CLASSNAME) VALUES
    (0, 'XWiki.Admin', 'XWiki.XWikiUsers'),
    (0, 'XWiki.editor', 'XWiki.XWikiUsers'),
    (0, 'XWiki.viewer', 'XWiki.XWikiUsers'),
    (0, 'XWiki.scriptuser', 'XWiki.XWikiUsers'),
    (0, 'Main.WebHome', 'XWiki.DocumentMetaClass'),
    (0, 'Sandbox.WebHome', 'XWiki.DocumentMetaClass');

-- Populate string properties (this is where sensitive config lives)
INSERT INTO xwikistrings (XWS_ID, XWS_NAME, XWS_VALUE) VALUES
    (1, 'first_name', 'Wiki'),
    (1, 'last_name', 'Admin'),
    (1, 'email', 'admin@xwiki.local'),
    (2, 'first_name', 'Content'),
    (2, 'last_name', 'Editor'),
    (2, 'email', 'editor@xwiki.local'),
    (3, 'first_name', 'Read'),
    (3, 'last_name', 'Only'),
    (4, 'first_name', 'Script'),
    (4, 'last_name', 'Developer'),
    (5, 'wiki.title', 'XWiki Platform'),
    (5, 'wiki.version', '16.4.5'),
    (6, 'secret_token', 'PLACEHOLDER_FLAG');

-- Group memberships
INSERT INTO xwikigroups (XWG_GROUPNAME, XWG_MEMBER) VALUES
    ('XWiki.XWikiAdminGroup', 'XWiki.Admin'),
    ('XWiki.XWikiAllGroup', 'XWiki.Admin'),
    ('XWiki.XWikiAllGroup', 'XWiki.editor'),
    ('XWiki.XWikiAllGroup', 'XWiki.viewer'),
    ('XWiki.XWikiAllGroup', 'XWiki.scriptuser'),
    ('XWiki.ScriptGroup', 'XWiki.scriptuser'),
    ('XWiki.ScriptGroup', 'XWiki.editor');

GRANT SELECT, INSERT, UPDATE ON xwiki.* TO 'xwikiuser'@'%';
FLUSH PRIVILEGES;
