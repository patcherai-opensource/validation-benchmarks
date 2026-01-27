CREATE DATABASE db;

CREATE USER 'db_username'@'%' IDENTIFIED BY 'pCxvkPyS9JYq27BVdUX4N8';

GRANT ALL PRIVILEGES ON db.* TO 'db_username'@'%';

FLUSH PRIVILEGES;

USE db;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'analyst'
);

CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(256) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Admin user with 'admin' role (password disabled for direct login)
INSERT INTO users (username, password, role) VALUES ('admin', 'NO_LOGIN_ALLOWED', 'admin');

-- Admin reports containing sensitive data
INSERT INTO reports (user_id, title, content) VALUES
(1, 'System Configuration', 'DataViz Analytics Platform Configuration Report'),
(1, 'Confidential API Keys', '@FLAG@'),
(1, 'Quarterly Revenue Analysis', 'Q4 2023 Revenue: $2.4M (+15% YoY)');
