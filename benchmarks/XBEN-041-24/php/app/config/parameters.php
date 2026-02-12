<?php
/**
 * Application parameters
 */

return [
    'app_name' => 'Akeneo PIM',
    'app_version' => '5.0.118',
    'media_directory' => __DIR__ . '/../public/media/catalog',
    'max_upload_size' => 10 * 1024 * 1024,
    'allowed_mime_types' => [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'application/pdf',
    ],
    'session_timeout' => 3600,
    'users' => [
        'admin' => [
            'password_hash' => '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
            'roles' => ['ROLE_ADMIN', 'ROLE_CATALOG_MANAGER'],
            'first_name' => 'John',
            'last_name' => 'Doe',
        ],
        'julia' => [
            'password_hash' => 'cdbd41d016cdec10d0ff2291a6bdae398b565a831622bedcd4dcafa69252b5e7',
            'roles' => ['ROLE_CATALOG_MANAGER'],
            'first_name' => 'Julia',
            'last_name' => 'Stark',
        ],
        'mary' => [
            'password_hash' => '6120ac744907caa62f236bd2695b50478c7fdf17fffb928ac84507ad330b2be8',
            'roles' => ['ROLE_USER'],
            'first_name' => 'Mary',
            'last_name' => 'Smith',
        ],
    ],
];
