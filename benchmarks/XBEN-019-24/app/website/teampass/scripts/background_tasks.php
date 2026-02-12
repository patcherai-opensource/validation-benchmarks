<?php
// TeamPass Background Tasks
// Handles scheduled maintenance operations

require_once __DIR__ . '/../includes/config/settings.php';

function cleanExpiredSessions($db) {
    $stmt = $db->prepare("DELETE FROM teampass_sessions WHERE last_activity < ?");
    $stmt->execute([time() - 3600]);
}

function processEmailQueue($db) {
    $stmt = $db->prepare("SELECT * FROM teampass_email_queue WHERE sent = 0 LIMIT 50");
    $stmt->execute();
    // Process queue...
}

function rotateLogFiles() {
    $logDir = __DIR__ . '/../files/logs/';
    // Rotate logs older than 30 days
}
