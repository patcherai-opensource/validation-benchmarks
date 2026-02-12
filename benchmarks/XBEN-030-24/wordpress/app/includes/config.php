<?php
/**
 * RaspAP configuration
 */

define('RASPI_VERSION', '2.8.9');
define('RASPI_CONFIG_DIR', '/etc/raspap');
define('RASPI_ADMIN_USER', 'admin');
define('RASPI_ADMIN_PASS', '$2y$10$hwxqYsCfsiLk5tCOOcZVLObKcQX27l90l51nN2KynsRnD1iAqWQFS'); // default
define('RASPI_SESSION_TIMEOUT', 3600);
define('RASPI_APP_NAME', 'RaspAP');
define('RASPI_WIFI_AP_INTERFACE', 'wlan0');
define('RASPI_WG_PORT', 51820);

// CSRF token generation
function generateCsrfToken() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function validateCsrfToken($token) {
    return isset($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token);
}

function isAuthenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}
