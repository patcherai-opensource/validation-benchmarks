<?php
// TeamPass Settings Loader
// Loads configuration from tp.config.php

if (!defined('TP_LOADED')) {
    define('TP_LOADED', true);
}

$config_file = __DIR__ . '/tp.config.php';
if (!file_exists($config_file)) {
    die('Configuration file not found. Please run the installer.');
}

$SETTINGS = require $config_file;

// Set timezone
date_default_timezone_set('UTC');

// Error reporting for production
error_reporting(0);
ini_set('display_errors', 0);
