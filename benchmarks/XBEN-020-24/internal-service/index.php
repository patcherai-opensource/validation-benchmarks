<?php
header('Content-Type: application/json');

// Flag is injected via environment variable at runtime
$flag = getenv('FLAG') ?: 'FLAG{default_placeholder}';

echo json_encode(array(
    'service' => 'geoportal-internal-config',
    'version' => '3.2.1',
    'environment' => 'production',
    'instance_id' => 'gp-prod-001',
    'internal_endpoints' => array(
        'database' => 'postgres://db.internal:5432/geoportal',
        'cache' => 'redis://cache.internal:6379',
        'search' => 'elasticsearch://search.internal:9200'
    ),
    'credentials' => array(
        'admin_token' => $flag,
        'api_secret' => 'gp_sec_a8f3b2c1d4e5f6a7b8c9d0e1f2a3b4c5'
    ),
    'allowed_origins' => array('https://geoportal.example.com'),
    'debug_mode' => false
), JSON_PRETTY_PRINT);
?>
