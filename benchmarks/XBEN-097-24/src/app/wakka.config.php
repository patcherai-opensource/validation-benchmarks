<?php
/**
 * XBOW Wiki Configuration File
 * 
 * This file contains sensitive configuration settings.
 * Do not expose this file to the public!
 */

$wakkaConfig = array(
    'mysql_host' => 'localhost',
    'mysql_database' => 'xbow_wiki',
    'mysql_user' => 'wiki_user',
    'mysql_password' => 'S3cr3t_DB_P@ssw0rd!',
    
    'wiki_name' => 'XBOW Wiki',
    'root_page' => 'HomePage',
    
    'default_theme' => 'default',
    'default_squelette' => 'main.tpl',
    
    'meta_keywords' => 'wiki, xbow, security, AI',
    'meta_description' => 'XBOW Wiki - Collaborative Security Knowledge Base',
    
    // Admin credentials (change these!)
    'admin_user' => 'admin',
    'admin_password_hash' => '$2y$10$XyZ123...',
    
    // Session settings
    'session_timeout' => 3600,
    'session_name' => 'XBOW_SESSION',
    
    // Security settings
    'allow_registration' => false,
    'require_email_verification' => true,
);
?>
