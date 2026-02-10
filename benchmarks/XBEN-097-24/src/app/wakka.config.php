<?php
/**
 * XBow Wiki Configuration File
 * 
 * This file loads configuration from the secure config directory
 */

// Load database configuration from secure location
$configPath = '/var/www/config/database.conf';
if (file_exists($configPath)) {
    $lines = file($configPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos($line, '=') !== false && $line[0] !== '#') {
            list($key, $value) = explode('=', $line, 2);
            $wakkaConfig[trim($key)] = trim($value);
        }
    }
}

// Default site settings
$wakkaConfig['base_url'] = 'https://wiki.xbow.local/';
$wakkaConfig['site_name'] = 'XBow Wiki';
$wakkaConfig['default_theme'] = 'default';
$wakkaConfig['wakka_version'] = '4.5.1';
