-- backup.sql - phpMyFAQ-inspired Knowledge Base

-- Users table with permissions
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
   `id` int NOT NULL AUTO_INCREMENT,
   `username` varchar(50) NOT NULL,
   `password` varchar(255) NOT NULL,
   `can_view_faq` tinyint(1) DEFAULT 1,
   `can_edit_faq` tinyint(1) DEFAULT 0,
   `can_add_faq` tinyint(1) DEFAULT 0,
   `is_admin` tinyint(1) DEFAULT 0,
   PRIMARY KEY (`id`),
   UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert default users: admin has all permissions, editor only has edit
INSERT INTO `users` VALUES 
   (1, 'admin', '$2y$10$9DT5Zq/G7XoYAwVGW8cFrerUQDkduPSYR0FMlmW.cWJCqoH/Ch5Iq', 1, 1, 1, 1),
   (2, 'editor', '$2y$10$be5zhgp7unwsxNgHA3FW8ui8LLQuxsBgM4sS4q/WUpMujR7OkYH5m', 1, 1, 0, 0);
-- admin password: admin123
-- editor password: editor123

-- FAQ categories
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories` (
   `id` int NOT NULL AUTO_INCREMENT,
   `name` varchar(100) NOT NULL,
   `description` text,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `categories` VALUES 
   (1, 'General', 'General FAQ items'),
   (2, 'Technical', 'Technical support questions'),
   (3, 'Billing', 'Billing and payment questions');

-- FAQ entries
DROP TABLE IF EXISTS `faqs`;
CREATE TABLE `faqs` (
   `id` int NOT NULL AUTO_INCREMENT,
   `category_id` int NOT NULL,
   `question` varchar(500) NOT NULL,
   `answer` text NOT NULL,
   `created_by` int,
   `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `faqs` VALUES 
   (1, 1, 'How do I create an account?', 'Click on Sign Up and fill in your details.', 1, NOW()),
   (2, 1, 'How do I reset my password?', 'Use the Forgot Password link on the login page.', 1, NOW()),
   (3, 2, 'What browsers are supported?', 'We support Chrome, Firefox, Safari, and Edge.', 1, NOW());

-- System configuration including flag
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
   `id` int NOT NULL AUTO_INCREMENT,
   `config_key` varchar(100) NOT NULL,
   `config_value` text,
   PRIMARY KEY (`id`),
   UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- The flag is stored as a "system secret" only visible to users who can add FAQs (admin level)
INSERT INTO `system_config` VALUES 
   (1, 'site_name', 'KnowledgeBase Pro'),
   (2, 'admin_email', 'admin@example.com'),
   (3, 'system_secret', '${FLAG}');
