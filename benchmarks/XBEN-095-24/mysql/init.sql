CREATE DATABASE IF NOT EXISTS teampass;
CREATE USER 'ctfuser'@'%' IDENTIFIED BY 'MyPass1234';

USE teampass;

-- Teampass users table
DROP TABLE IF EXISTS teampass_users;
CREATE TABLE teampass_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    login VARCHAR(256) NOT NULL,
    pw VARCHAR(256) NOT NULL,
    admin INT DEFAULT 0,
    email VARCHAR(256),
    name VARCHAR(256),
    lastname VARCHAR(256),
    can_manage_all_users INT DEFAULT 0,
    last_pw_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    isAdministratedByRole INT DEFAULT 0,
    disabled INT DEFAULT 0,
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    special VARCHAR(256) DEFAULT NULL,
    auth_type VARCHAR(50) DEFAULT 'local'
);

-- Teampass nested tree (folders structure)
DROP TABLE IF EXISTS teampass_nested_tree;
CREATE TABLE teampass_nested_tree (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parent_id INT DEFAULT 0,
    title VARCHAR(256) NOT NULL,
    nleft INT DEFAULT 0,
    nright INT DEFAULT 0,
    nlevel INT DEFAULT 0,
    bloquer_creation INT DEFAULT 0,
    bloquer_modification INT DEFAULT 0,
    personal_folder INT DEFAULT 0
);

-- Teampass items (passwords stored in the manager)
DROP TABLE IF EXISTS teampass_items;
CREATE TABLE teampass_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    label VARCHAR(500) NOT NULL,
    description TEXT,
    pw VARCHAR(500),
    pw_iv VARCHAR(500),
    url VARCHAR(500),
    id_tree INT,
    login VARCHAR(200),
    inactif INT DEFAULT 0,
    perso INT DEFAULT 0,
    restricted_to VARCHAR(200),
    anyone_can_modify INT DEFAULT 0,
    email VARCHAR(500) DEFAULT NULL,
    notification VARCHAR(500) DEFAULT NULL,
    viewed_no INT DEFAULT 0,
    complexity_level INT DEFAULT 0,
    auto_update_pwd_frequency INT DEFAULT 0,
    auto_update_pwd_next_date INT DEFAULT 0,
    encryption_type VARCHAR(50) DEFAULT 'teampass_aes',
    fa_icon VARCHAR(100) DEFAULT NULL
);

-- Teampass API keys table
DROP TABLE IF EXISTS teampass_api;
CREATE TABLE teampass_api (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(15) NOT NULL,
    label VARCHAR(255),
    value TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    allowed_folders TEXT DEFAULT NULL,
    enabled INT DEFAULT 1,
    read_only INT DEFAULT 0
);

-- Teampass log table  
DROP TABLE IF EXISTS teampass_log_system;
CREATE TABLE teampass_log_system (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    label TEXT,
    qui VARCHAR(255),
    field_1 VARCHAR(255) DEFAULT NULL
);

-- Teampass settings (misc)
DROP TABLE IF EXISTS teampass_misc;
CREATE TABLE teampass_misc (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50) NOT NULL,
    intitule VARCHAR(255) NOT NULL,
    valeur TEXT
);

-- Insert default users (passwords are bcrypt hashed)
INSERT INTO teampass_users (login, pw, admin, email, name, lastname, auth_type) VALUES
    ('admin', '$2y$10$u5XQfUEcGLHRqGE7TR6H5OX1PkdS0r7jHj.oWcKHvcCzQcr1pQ2D2', 1, 'admin@teampass.local', 'Admin', 'User', 'local'),
    ('manager', '$2y$10$1OKQz3H0GYb6P7eFkPHOCOiVJQjD5rZ6Y1.8xPv0fF.cIe7jJ1RPe', 0, 'manager@teampass.local', 'Project', 'Manager', 'local'),
    ('readonly', '$2y$10$J5x5IZQkXgKTn4l0c0CbYOaVGBxJnkdJXlJxpNe4yF5cLk7bMJ3Oi', 0, 'readonly@teampass.local', 'Read', 'Only', 'local'),
    ('john.doe', '$2y$10$Wt3bR0xnGO4Mh8f9m0y5DOjKlVh6CEGNG0fBHVnRe7gT0Hw1XQaCi', 0, 'john@teampass.local', 'John', 'Doe', 'local');

-- Insert folder structure
INSERT INTO teampass_nested_tree (parent_id, title, nleft, nright, nlevel) VALUES
    (0, 'Servers', 1, 6, 1),
    (1, 'Production', 2, 3, 2),
    (1, 'Staging', 4, 5, 2),
    (0, 'Databases', 7, 10, 1),
    (4, 'MySQL Instances', 8, 9, 2),
    (0, 'Cloud Services', 11, 14, 1),
    (6, 'AWS', 12, 13, 2);

-- Insert sample items (passwords)
INSERT INTO teampass_items (label, description, pw, url, id_tree, login, encryption_type) VALUES
    ('Production Web Server', 'Main production server SSH access', 'enc_R3dH4t!2023_iv_a1b2c3', 'ssh://prod-web-01.internal', 2, 'sysadmin', 'teampass_aes'),
    ('Staging Web Server', 'Staging environment SSH', 'enc_St4g1ng#Pass_iv_d4e5f6', 'ssh://staging-01.internal', 3, 'deploy', 'teampass_aes'),
    ('MySQL Production', 'Production database root access', 'enc_MyS3cure!DB_iv_g7h8i9', 'mysql://db-prod.internal:3306', 5, 'root', 'teampass_aes'),
    ('MySQL Staging', 'Staging database', 'enc_St4geDB_iv_j0k1l2', 'mysql://db-staging.internal:3306', 5, 'dbadmin', 'teampass_aes'),
    ('AWS Console', 'Main AWS account', 'enc_Cl0ud!Mgr_iv_m3n4o5', 'https://console.aws.amazon.com', 7, 'cloudadmin@company.com', 'teampass_aes'),
    ('S3 Backup Bucket', 'Backup storage credentials', 'enc_B4ckupK3y_iv_p6q7r8', 'https://s3.amazonaws.com/company-backups', 7, 'backup-svc', 'teampass_aes');

-- Insert API keys
INSERT INTO teampass_api (type, label, value, enabled, read_only, allowed_folders) VALUES
    ('user', 'monitoring-api-key', 'ak_mon_7f3e2d1c9b8a', 1, 1, '1,2'),
    ('user', 'ci-deploy-key', 'ak_deploy_4e5f6a7b8c9d', 1, 0, '2,3'),
    ('admin', 'master-integration-key', '__FLAG_PLACEHOLDER__', 1, 0, NULL);

-- Insert some settings
INSERT INTO teampass_misc (type, intitule, valeur) VALUES
    ('admin', 'teampass_version', '3.0.0.21'),
    ('admin', 'cpassman_dir', '/var/www/html'),
    ('admin', 'cpassman_url', 'https://teampass.local'),
    ('admin', 'saltkey_ante_2127', 'a1b2c3d4e5f6'),
    ('admin', 'enable_api', '1'),
    ('admin', 'api_token_duration', '60'),
    ('admin', 'duo_enabled', '0'),
    ('admin', 'ldap_mode', '0'),
    ('admin', 'anyone_can_modify', '0'),
    ('admin', 'nb_items_by_query', '3');

-- Insert some log entries
INSERT INTO teampass_log_system (type, label, qui) VALUES
    ('admin_action', 'System initialized', 'admin'),
    ('admin_action', 'API enabled', 'admin'),
    ('user_connection', 'User connected', 'admin');

GRANT SELECT ON teampass.* TO 'ctfuser'@'%';
FLUSH PRIVILEGES;
