<?php
/**
 * ImageOptimizer Backend Configuration Sample
 * Copy to config.php and customize
 */

return [
    'service_name' => 'ImageOptimizer Backend',
    'version' => '1.2.3',
    
    // Storage settings
    'upload_dir' => '/tmp',
    'max_file_size' => 52428800, // 50MB
    
    // Supported formats
    'allowed_formats' => ['jpg', 'jpeg', 'png', 'gif', 'webp', 'avif'],
    
    // Optimizer chain
    'optimizers' => [
        'jpeg' => ['jpegoptim', 'jpegtran'],
        'png' => ['optipng', 'pngquant'],
        'gif' => ['gifsicle'],
        'webp' => ['cwebp'],
    ],
    
    // Processing callbacks (for ImageProcessor class)
    // WARNING: Callbacks are eval'd - ensure they come from trusted sources
    'post_process_callback' => null,
    
    // Security settings
    'allowed_networks' => ['172.0.0.0/8'],
];
