<?php
header('Content-Type: application/json');
echo json_encode([
    'service' => 'GeoPortal',
    'version' => '3.4.2',
    'api_version' => '2.1',
    'capabilities' => [
        'WMS' => ['1.1.1', '1.3.0'],
        'WFS' => ['1.0.0', '1.1.0', '2.0.0'],
        'WMTS' => ['1.0.0'],
        'CSW' => ['2.0.2']
    ],
    'features' => [
        'proxy' => true,
        'tile_cache' => true,
        'user_uploads' => false,
        'public_maps' => true
    ],
    'limits' => [
        'max_upload_size' => '100MB',
        'rate_limit' => '1000 requests/hour'
    ]
], JSON_PRETTY_PRINT);
?>
