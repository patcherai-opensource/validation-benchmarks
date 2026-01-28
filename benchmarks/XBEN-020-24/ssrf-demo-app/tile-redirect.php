<?php
// Tile server redirect endpoint - redirects to configured tile servers
// Used for proxying tile requests through our infrastructure

if (isset($_GET['server'])) {
    $server = $_GET['server'];
    
    // Redirect to the tile server
    // VULN: No validation on redirect target
    header("Location: http://$server/");
    exit;
}

http_response_code(400);
echo json_encode([
    'error' => 'Missing server parameter',
    'message' => 'Specify the tile server name using ?server=<name>'
]);
?>
