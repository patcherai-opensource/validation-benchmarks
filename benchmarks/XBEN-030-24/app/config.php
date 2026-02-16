<?php
define('APP_ROOT', __DIR__);
define('APP_VERSION', '18.0.4');
define('APP_NAME', 'GestiPro ERP');

$db_host = getenv('DB_HOST') ?: '127.0.0.1';
$db_name = getenv('DB_NAME') ?: 'challenge';
$db_user = getenv('DB_USER') ?: 'gestipro';
$db_pass = getenv('DB_PASSWORD') ?: 'gestipro';
$db_port = getenv('DB_PORT') ?: '3306';

function get_db() {
    global $db_host, $db_name, $db_user, $db_pass, $db_port;
    static $pdo = null;
    if ($pdo === null) {
        $dsn = "mysql:host={$db_host};port={$db_port};dbname={$db_name};charset=utf8mb4";
        $pdo = new PDO($dsn, $db_user, $db_pass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
    }
    return $pdo;
}

function get_conf_value($key) {
    try {
        $db = get_db();
        $stmt = $db->prepare("SELECT value FROM gp_settings WHERE name = ?");
        $stmt->execute([$key]);
        $row = $stmt->fetch();
        return $row ? $row['value'] : '';
    } catch (Exception $e) {
        return '';
    }
}
