<?php
/**
 * Dolibarr ERP & CRM - Configuration file
 *
 * @package  Dolibarr
 */

// Database configuration
$dolibarr_main_db_host = getenv('DB_HOST') ?: '127.0.0.1';
$dolibarr_main_db_port = getenv('DB_PORT') ?: '3306';
$dolibarr_main_db_name = getenv('DB_NAME') ?: 'dolibarr';
$dolibarr_main_db_prefix = 'llx_';
$dolibarr_main_db_user = getenv('DB_USER') ?: 'dolibarr';
$dolibarr_main_db_pass = getenv('DB_PASSWORD') ?: 'dolibarr';
$dolibarr_main_db_type = 'mysqli';
$dolibarr_main_db_character_set = 'utf8';
$dolibarr_main_db_collation = 'utf8_unicode_ci';

// Application paths
$dolibarr_main_url_root = '';
$dolibarr_main_document_root = '/var/www/html/htdocs';
$dolibarr_main_data_root = '/var/www/html/documents';

// Security
$dolibarr_main_authentication = 'dolibarr';
$dolibarr_main_force_https = '0';

// Misc
$dolibarr_main_prod = '1';
$dolibarr_main_cookie_cryptkey = 'a8f2e9c4b7d1053f6e8a9b2c4d7f1a3e5b8c0d2f4a6e8b1c3d5f7a9b0c2d4e6';
$dolibarr_main_instance_unique_id = 'erp-prod-19a4c3e8';
