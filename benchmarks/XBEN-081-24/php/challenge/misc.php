<?php

function validateInput($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

function formatTimestamp($timestamp) {
    $dt = new DateTime($timestamp);
    $now = new DateTime();
    $diff = $now->getTimestamp() - $dt->getTimestamp();

    if ($diff < 60) return 'just now';
    if ($diff < 3600) return floor($diff / 60) . 'm ago';
    if ($diff < 86400) return floor($diff / 3600) . 'h ago';
    return $dt->format('M j, Y');
}

?>
