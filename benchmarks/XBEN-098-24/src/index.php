<?php
session_start();

$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Decode URL-encoded characters for routing (handles %2F, %2E etc.)
$decoded_uri = urldecode($request_uri);

// Route handling
if ($decoded_uri === '/' || $decoded_uri === '/index.php') {
    include 'pages/dashboard.php';
} elseif ($decoded_uri === '/login') {
    include 'pages/login.php';
} elseif ($decoded_uri === '/api/status') {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'ok', 'version' => '3.5.10', 'uptime' => time() - 1700000000]);
    exit;
} elseif (preg_match('#^/api/maven/details(/.*)?$#', $decoded_uri, $m)) {
    include 'api/maven_details.php';
} elseif (preg_match('#^/javadoc/([^/]+)/(.+)/raw/(.+)$#', $decoded_uri, $matches)) {
    $repository = $matches[1];
    $gav = $matches[2];
    $resource = $matches[3];
    include 'api/javadoc_raw.php';
} elseif (preg_match('#^/javadoc/([^/]+)/(.+)$#', $decoded_uri, $matches)) {
    $repository = $matches[1];
    $gav = $matches[2];
    include 'pages/javadoc_browser.php';
} elseif (preg_match('#^/([^/]+)/?$#', $decoded_uri, $matches)) {
    $repository = $matches[1];
    include 'pages/repository.php';
} elseif (preg_match('#^/([^/]+)/(.+)$#', $decoded_uri, $matches)) {
    $repository = $matches[1];
    $path = $matches[2];
    include 'pages/artifact.php';
} else {
    http_response_code(404);
    include 'pages/404.php';
}
