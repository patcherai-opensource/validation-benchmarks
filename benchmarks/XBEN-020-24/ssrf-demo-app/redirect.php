<?php
// Legacy redirect endpoint - deprecated, use /proxy/ instead
header('HTTP/1.1 410 Gone');
echo json_encode([
    'error' => 'This endpoint has been deprecated',
    'message' => 'Please use the proxy API endpoint for external resource fetching',
    'documentation' => '/api/'
]);
?>
