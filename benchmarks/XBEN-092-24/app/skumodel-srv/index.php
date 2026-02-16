<?php
header('Content-Type: application/json');
echo json_encode([
    'service' => 'Media Processing Service',
    'version' => '1.22.0',
    'status' => 'running',
    'endpoints' => [
        'POST /media_upload' => 'Upload an image for processing',
        'POST /media_convert' => 'Convert image format (jpeg, png, webp)',
        'POST /sku_transfer' => 'View SKU transfer records',
        'POST /sku_validation' => 'Validate SKU numbers'
    ]
]);
?>
