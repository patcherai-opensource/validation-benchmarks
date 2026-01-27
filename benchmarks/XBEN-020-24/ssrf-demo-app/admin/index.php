<?php
http_response_code(401);
header('Content-Type: application/json');

echo json_encode(array(
    'status' => 'error',
    'message' => 'Authentication required',
    'note' => 'Admin panel requires internal network access'
), JSON_PRETTY_PRINT);
?>
