<?php
header('Content-Type: application/json');

/**
 * Service Health & Diagnostics
 * Returns service status and component information.
 */

$response = [
    'status' => 'healthy',
    'service' => 'Media Processing Service',
    'version' => '1.22.0',
    'php_version' => PHP_VERSION,
    'extensions' => [
        'gd' => extension_loaded('gd'),
        'phar' => extension_loaded('phar')
    ],
    'components' => [
        'CacheManager' => 'Cache lifecycle handler',
        'ImageMetadata' => 'Image metadata container'
    ],
    'upload_dir' => '/var/www/html/uploads',
    'max_upload_size' => '16M'
];

echo json_encode($response);
?>
