<?php
session_start();
require_once __DIR__ . '/../../includes/config.php';

header('Content-Type: application/json');

// Require authentication
if (!isAuthenticated()) {
    http_response_code(403);
    echo json_encode(array('error' => 'Not authenticated'));
    exit;
}

// Validate CSRF token
if (!isset($_POST['csrf_token']) || !validateCsrfToken($_POST['csrf_token'])) {
    http_response_code(403);
    echo json_encode(array('error' => 'CSRF token validation failed'));
    exit;
}

if (!isset($_POST['entity']) || empty($_POST['entity'])) {
    http_response_code(400);
    echo json_encode(array('error' => 'Missing required parameter: entity'));
    exit;
}

$entity = $_POST['entity'];

$privkey_tmp = '/tmp/'.$entity.'-private.key';
$pubkey_tmp = '/tmp/'.$entity.'-public.key';

$return = array();
exec("sudo wg genkey | tee $privkey_tmp | wg pubkey > $pubkey_tmp", $return);

$pubkey = @file_get_contents($pubkey_tmp);
$privkey = @file_get_contents($privkey_tmp);

$result = array(
    'return' => 0,
    'pubkey' => $pubkey !== false ? trim($pubkey) : '',
    'privkey' => $privkey !== false ? trim($privkey) : '',
    'output' => 'Keys generated for ' . htmlspecialchars($entity)
);

echo json_encode($result);
