<?php
session_start();
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/functions.php';

header('Content-Type: application/json');

if (!isAuthenticated()) {
    http_response_code(403);
    echo json_encode(array('error' => 'Not authenticated'));
    exit;
}

if (!isset($_POST['csrf_token']) || !validateCsrfToken($_POST['csrf_token'])) {
    http_response_code(403);
    echo json_encode(array('error' => 'CSRF token validation failed'));
    exit;
}

$iface = isset($_POST['iface']) ? sanitizeFilename($_POST['iface']) : 'eth0';

$result = array(
    'interface' => $iface,
    'addresses' => array(),
    'status' => 'unknown'
);

$output = array();
exec('ip -j addr show ' . escapeshellarg($iface) . ' 2>/dev/null', $output);

if (!empty($output)) {
    $data = json_decode(implode('', $output), true);
    if ($data && is_array($data)) {
        $result['status'] = 'up';
        foreach ($data as $entry) {
            if (isset($entry['addr_info'])) {
                foreach ($entry['addr_info'] as $addr) {
                    $result['addresses'][] = array(
                        'family' => $addr['family'] ?? '',
                        'local' => $addr['local'] ?? '',
                        'prefixlen' => $addr['prefixlen'] ?? 0
                    );
                }
            }
        }
    }
}

echo json_encode($result);
