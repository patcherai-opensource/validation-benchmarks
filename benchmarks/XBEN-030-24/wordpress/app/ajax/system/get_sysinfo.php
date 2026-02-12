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

$info = getSystemInfo();

$loadavg = @file_get_contents('/proc/loadavg');
$loads = $loadavg ? explode(' ', $loadavg) : array('0', '0', '0');

$meminfo = @file_get_contents('/proc/meminfo');
$memtotal = 0;
$memfree = 0;
if ($meminfo) {
    preg_match('/MemTotal:\s+(\d+)/', $meminfo, $m);
    $memtotal = isset($m[1]) ? intval($m[1]) : 0;
    preg_match('/MemAvailable:\s+(\d+)/', $meminfo, $m);
    $memfree = isset($m[1]) ? intval($m[1]) : 0;
}

$result = array(
    'hostname' => $info['hostname'],
    'kernel' => $info['kernel'],
    'uptime' => $info['uptime'],
    'load' => array(
        '1min' => floatval($loads[0]),
        '5min' => floatval($loads[1]),
        '15min' => floatval($loads[2])
    ),
    'memory' => array(
        'total' => $memtotal,
        'available' => $memfree,
        'used' => $memtotal - $memfree,
        'percent' => $memtotal > 0 ? round((($memtotal - $memfree) / $memtotal) * 100) : 0
    )
);

echo json_encode($result);
