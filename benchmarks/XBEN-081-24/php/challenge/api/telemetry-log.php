<?php
    // Telemetry log reader - returns recent telemetry events
    header('Content-Type: application/json');

    $log_file = '/tmp/telemetry/events.log';

    if (!file_exists($log_file)) {
        echo json_encode(['events' => []]);
        exit();
    }

    $lines = file($log_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    $events = [];
    foreach (array_slice($lines, -50) as $line) {
        $event = json_decode($line, true);
        if ($event) {
            $events[] = $event;
        }
    }

    echo json_encode(['events' => $events]);
