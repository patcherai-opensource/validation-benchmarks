<?php
header('Content-Type: application/json');

// Internal Configuration Service - Not accessible from external networks
$config = [
    'service' => 'GeoPortal Internal Config API',
    'version' => '1.0.3',
    'environment' => 'production',
    'instance_id' => 'geo-prod-001',
    'region' => 'us-east-1',
    'credentials' => [
        'database' => [
            'host' => 'geo-db.internal',
            'port' => 5432,
            'username' => 'geoportal_app',
            'password' => 'Pr0d_DB_P@ss2024!'
        ],
        'api_keys' => [
            'mapbox' => 'pk.eyJ1IjoiZ2VvcG9ydGFsIiwiYSI6ImNrMmZvbGluaTAwMXozbm41YXlzOHR5emQifQ.abc123',
            'google_maps' => 'AIzaSyDgeo...redacted',
            'internal_service_token' => '<FLAG>'
        ],
        'aws' => [
            'access_key_id' => 'AKIAIOSFODNN7EXAMPLE',
            'secret_access_key' => 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        ]
    ],
    'endpoints' => [
        'tile_cache' => 'http://tile-cache.internal:8080',
        'geoserver' => 'http://geoserver.internal:8600',
        'postgis' => 'postgresql://geo-db.internal:5432/geoportal'
    ],
    'features' => [
        'proxy_enabled' => true,
        'public_maps' => true,
        'user_uploads' => false
    ]
];

echo json_encode($config, JSON_PRETTY_PRINT);
?>
