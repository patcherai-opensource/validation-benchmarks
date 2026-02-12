<?php
    $db_host = getenv('DB_HOST') ?: 'localhost';
    $db_database = getenv('DB_DATABASE') ?: 'app_db';
    $db_username = getenv('DB_USERNAME') ?: 'db_username';
    $db_password = getenv('DB_PASSWORD') ?: 'pCxvkPyS9JYq27BVdUX4N8';

    // Cookie configuration
    define('ADMIN_REMEMBER_ME_COOKIE_NAME', 'armcn');
    define('CUSTOMER_REMEMBER_ME_COOKIE_NAME', 'crmcn');
    define('COOKIE_EXPIRY', 60 * 60 * 24 * 30); // 30 days
?>
