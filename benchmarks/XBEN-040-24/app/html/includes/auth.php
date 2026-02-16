<?php
session_start();

function require_auth() {
    if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
        header('Location: login.php');
        exit;
    }
}

function get_db_connection() {
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'nmsdb';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        http_response_code(500);
        die('Database connection failed.');
    }
    return $conn;
}

function is_authenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}
