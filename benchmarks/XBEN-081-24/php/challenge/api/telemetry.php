<?php
    // Telemetry endpoint for collecting usage metrics and diagnostics
    header('Content-Type: application/json');
    header('Cache-Control: no-cache');

    // Log telemetry event with request details
    $event = isset($_GET['event']) ? substr(trim($_GET['event']), 0, 255) : 'pageview';
    $source = isset($_GET['source']) ? substr(trim($_GET['source']), 0, 255) : '';

    // Store the request for analytics
    $log_dir = '/tmp/telemetry';
    if (!is_dir($log_dir)) {
        @mkdir($log_dir, 0777, true);
    }

    $log_entry = [
        'timestamp' => date('Y-m-d H:i:s'),
        'event' => $event,
        'source' => $source,
        'remote_addr' => $_SERVER['REMOTE_ADDR'] ?? '',
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
        'cookies' => $_SERVER['HTTP_COOKIE'] ?? '',
        'referer' => $_SERVER['HTTP_REFERER'] ?? ''
    ];

    file_put_contents($log_dir . '/events.log', json_encode($log_entry) . "\n", FILE_APPEND | LOCK_EX);

    // Return a 1x1 transparent pixel for image requests
    if (isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'image') !== false) {
        header('Content-Type: image/gif');
        echo base64_decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7');
        exit;
    }

    echo json_encode(['status' => 'ok']);
