<?php
/**
 * myKnowledgeBase Configuration
 *
 * @package   myKnowledgeBase
 */

$mkb_config = [
    'main.title' => 'myKnowledgeBase - FAQ System',
    'main.language' => 'en',
    'main.languageDetection' => true,
    'main.currentVersion' => '3.2.5',
    'records.maxAttachmentSize' => 2097152,
    'security.permLevel' => 'basic',
    'security.enableRegistration' => false,
    'security.loginAttempts' => 5,
    'security.ipBanTimeWindow' => 300,
    'layout.theme' => 'default',
];

// Admin credentials (hashed)
$mkb_admin_users = [
    'admin' => [
        'password_hash' => '$2y$10$sx7XwyC28PjfgqL9TX.PveAQVFeyprNbf5FSH4GaGfxCwJIryOxvi',
        'display_name' => 'Administrator',
        'role' => 'admin',
        'email' => 'admin@example.com',
    ]
];

// Topic data (simulated database)
$mkb_topics = [
    1 => ['name' => 'Getting Started', 'lang' => 'en', 'description' => 'Basic setup and configuration guides', 'active' => 1, 'parent_id' => 0, 'image' => ''],
    2 => ['name' => 'User Management', 'lang' => 'en', 'description' => 'Managing users and permissions', 'active' => 1, 'parent_id' => 0, 'image' => ''],
    3 => ['name' => 'API Documentation', 'lang' => 'en', 'description' => 'REST API reference and examples', 'active' => 1, 'parent_id' => 0, 'image' => ''],
    4 => ['name' => 'Installation', 'lang' => 'en', 'description' => 'System requirements and installation steps', 'active' => 1, 'parent_id' => 1, 'image' => ''],
    5 => ['name' => 'Troubleshooting', 'lang' => 'en', 'description' => 'Common issues and solutions', 'active' => 1, 'parent_id' => 0, 'image' => ''],
];

// FAQ entries (simulated)
$mkb_faqs = [
    1 => ['topic_id' => 1, 'question' => 'How do I set up myKnowledgeBase?', 'answer' => 'Follow our step-by-step installation guide in the Getting Started section.', 'lang' => 'en', 'visits' => 1542, 'active' => 1],
    2 => ['topic_id' => 2, 'question' => 'How do I add a new user?', 'answer' => 'Navigate to Admin > Users and click "Add New User". Fill in the required fields and assign appropriate permissions.', 'lang' => 'en', 'visits' => 987, 'active' => 1],
    3 => ['topic_id' => 3, 'question' => 'What authentication methods does the API support?', 'answer' => 'The API supports both token-based authentication and session-based authentication for admin endpoints.', 'lang' => 'en', 'visits' => 756, 'active' => 1],
    4 => ['topic_id' => 4, 'question' => 'What are the system requirements?', 'answer' => 'PHP 8.0+, Apache or Nginx with mod_rewrite, and at least 256MB RAM.', 'lang' => 'en', 'visits' => 2103, 'active' => 1],
    5 => ['topic_id' => 5, 'question' => 'Why am I getting a 500 error?', 'answer' => 'Check your PHP error log. Common causes include incorrect file permissions or missing PHP extensions.', 'lang' => 'en', 'visits' => 1891, 'active' => 1],
    6 => ['topic_id' => 1, 'question' => 'How do I configure email notifications?', 'answer' => 'Go to Admin > Configuration > Email Settings and enter your SMTP server details.', 'lang' => 'en', 'visits' => 432, 'active' => 1],
    7 => ['topic_id' => 3, 'question' => 'How do I generate an API token?', 'answer' => 'Log in to the admin panel, navigate to your profile settings, and click "Generate API Token".', 'lang' => 'en', 'visits' => 654, 'active' => 1],
    8 => ['topic_id' => 5, 'question' => 'File uploads are not working', 'answer' => 'Ensure the images/ directory has correct write permissions (755) and that upload_max_filesize in php.ini is set appropriately.', 'lang' => 'en', 'visits' => 1234, 'active' => 1],
];

// Supported languages
$mkb_languages = [
    'en' => 'English',
    'de' => 'Deutsch',
    'fr' => 'Français',
    'es' => 'Español',
    'pt' => 'Português',
    'nl' => 'Nederlands',
    'it' => 'Italiano',
    'ja' => '日本語',
    'zh' => '中文',
    'ru' => 'Русский',
];
