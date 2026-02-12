<?php
// TeamPass API Bootstrap
define('TP_VERSION', '3.0.9');
define('TP_API_VERSION', '1.0');

// Load configuration
if (file_exists(__DIR__ . '/../../includes/config/tp.config.php')) {
    $SETTINGS = require __DIR__ . '/../../includes/config/tp.config.php';
}

// Autoloader
spl_autoload_register(function ($class) {
    $prefix = 'TeamPass\\';
    $base_dir = __DIR__ . '/../';
    
    $len = strlen($prefix);
    if (strncmp($prefix, $class, $len) !== 0) {
        return;
    }
    
    $relative_class = substr($class, $len);
    $file = $base_dir . str_replace('\\', '/', $relative_class) . '.php';
    
    if (file_exists($file)) {
        require $file;
    }
});
