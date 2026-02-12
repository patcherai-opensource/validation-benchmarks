<?php
define('DB_HOST', getenv('MYSQL_HOST') ?: '127.0.0.1');
define('DB_USER', getenv('MYSQL_USER') ?: 'user');
define('DB_PASS', getenv('MYSQL_PASSWORD') ?: 'password');
define('DB_NAME', getenv('MYSQL_DATABASE') ?: 'pimcore');
define('PIMCORE_VERSION', '10.5.23');
define('PIMCORE_BUILD', '2023.07.15');

function get_db() {
    static $conn = null;
    if ($conn === null) {
        $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
        if ($conn->connect_error) {
            http_response_code(503);
            die(json_encode(['success' => false, 'message' => 'Service temporarily unavailable']));
        }
        $conn->set_charset('utf8mb4');
    }
    return $conn;
}

function check_admin_auth() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    if (!isset($_SESSION['pimcore_admin_user']) || !isset($_SESSION['pimcore_admin_sid'])) {
        if (is_api_request()) {
            http_response_code(403);
            header('Content-Type: application/json');
            die(json_encode(['success' => false, 'message' => 'Not authenticated - Session expired']));
        }
        header('Location: /admin/login.php');
        exit;
    }
}

function is_api_request() {
    return (
        (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest') ||
        (isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) ||
        (isset($_SERVER['CONTENT_TYPE']) && strpos($_SERVER['CONTENT_TYPE'], 'application/json') !== false)
    );
}

function json_response($data, $code = 200) {
    http_response_code($code);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit;
}

function extract_sorting_settings($request) {
    $settings = [];
    $sort = isset($request['sort']) ? $request['sort'] : null;
    if ($sort) {
        if (is_string($sort)) {
            $sort = json_decode($sort, true);
        }
        if (is_array($sort) && count($sort) > 0) {
            $firstSort = isset($sort[0]) ? $sort[0] : $sort;
            if (isset($firstSort['property'])) {
                $settings['orderKey'] = $firstSort['property'];
            }
            if (isset($firstSort['direction'])) {
                $settings['order'] = strtoupper($firstSort['direction']) === 'DESC' ? 'DESC' : 'ASC';
            }
        }
    }
    return $settings;
}
