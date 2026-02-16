<?php
define('DB_HOST', getenv('MYSQL_HOST') ?: '127.0.0.1');
define('DB_USER', getenv('MYSQL_USER') ?: 'vaultuser');
define('DB_PASS', getenv('MYSQL_PASSWORD') ?: 'Kx9$mP2vL7qR');
define('DB_NAME', getenv('MYSQL_DATABASE') ?: 'vaultpass');
define('DB_PORT', getenv('MYSQL_PORT') ?: '3306');

define('APP_NAME', 'VaultPass');
define('APP_VERSION', '3.0.0.21');
define('JWT_SECRET', 'vp_s3cr3t_k3y_f0r_t0k3n_s1gn1ng');

define('API_ROOT_PATH', __DIR__ . '/../api');

function db_connect() {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME, (int)DB_PORT);
    if ($conn->connect_error) {
        return null;
    }
    return $conn;
}
