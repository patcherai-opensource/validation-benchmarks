<?php
return [
    'db' => [
        'host' => getenv('DB_HOST') ?: '127.0.0.1',
        'name' => getenv('DB_NAME') ?: 'contentforge',
        'user' => getenv('DB_USER') ?: 'cfadmin',
        'password' => getenv('DB_PASSWORD') ?: 'cf_db_s3cure!',
        'port' => (int)(getenv('DB_PORT') ?: 3306),
    ],
    'auth' => [
        'defaultHashMethod' => 'StandardHashMethod',
        'enforceHashPolicy' => false,
        'sessionLifetime' => 3600,
    ],
    'site' => [
        'name' => 'ContentForge CMS',
        'version' => '4.2.1',
    ],
];
