<?php
header('Content-Type: application/json');

echo json_encode(array(
    'api' => 'GeoPortal API',
    'version' => '3.2.1',
    'endpoints' => array(
        '/api/layers' => 'List available map layers',
        '/api/search' => 'Search geographic features',
        '/proxy/' => 'Proxy external WMS/WFS requests'
    ),
    'documentation' => '/api/docs'
), JSON_PRETTY_PRINT);
?>
