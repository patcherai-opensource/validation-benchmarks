-- Create the database
CREATE DATABASE IF NOT EXISTS blogDB;
USE blogDB;

-- Create the table for blog posts
CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    image VARCHAR(255) NOT NULL,
    published TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for comments
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Create the table for admins
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create secrets table (not exposed through normal application UI)
-- This table stores sensitive configuration and API keys
CREATE TABLE secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(255) NOT NULL,
    key_value TEXT NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table (typical user data in a DB-GPT deployment)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_key VARCHAR(64),
    is_admin TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample posts
INSERT INTO posts (title, category, content, image, published) VALUES
('The Magic of Morning Dew', 'Nature', 'Experience the serene beauty of morning dew as it glistens on the fresh green leaves, transforming the ordinary garden into a sparkling jewel under the sunrise.', 'morning-dew.jpg',1),
('Sunset Serenades', 'Nature', 'As the sun sets, the sky turns a palette of deep oranges, fiery reds, and calming purples, offering a perfect backdrop for an evening under the stars.', 'sunset.jpg',1),
('Forest Whisperings', 'Nature', 'Walking through the forest, one can hear the whispers of ancient trees, rustling leaves telling tales of old in the crisp, clean air.', 'forest.jpg',1),
('Decoding Tech Trends', 'Tech', 'An analysis of emerging technology trends that will shape our future, from AI advancements to the rise of quantum computing.', 'tech-trends.jpg',1),
('Smartphone Evolution', 'Tech', 'A look back at the evolution of smartphones over the past decade, highlighting key innovations that have transformed how we communicate.', 'smartphones.jpg',1),
('The Future of Robotics', 'Tech', 'Exploring the potential impacts of robotics in various industries, and how they are set to revolutionize efficiency and productivity.', 'robotics.jpg',1);

-- Add admin user
INSERT INTO admins (username, password) VALUES ('admin', MD5('admin123'));

-- Add sample users
INSERT INTO users (username, email, password_hash, api_key, is_admin) VALUES
('admin', 'admin@dbgpt.local', MD5('admin123'), 'sk-admin-abc123def456', 1),
('analyst', 'analyst@dbgpt.local', MD5('analyst456'), 'sk-analyst-xyz789', 0),
('viewer', 'viewer@dbgpt.local', MD5('viewer789'), NULL, 0);

-- Insert secrets - including the flag as a sensitive API key
INSERT INTO secrets (key_name, key_value, description) VALUES
('OPENAI_API_KEY', 'sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'OpenAI API key for LLM integration'),
('DATABASE_ENCRYPTION_KEY', 'enc-key-9f8e7d6c5b4a3210', 'Master encryption key for database fields'),
('INTERNAL_SERVICE_TOKEN', '@FLAG@', 'Internal service authentication token - DO NOT EXPOSE'),
('AWS_SECRET_ACCESS_KEY', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY', 'AWS credentials for S3 storage');
