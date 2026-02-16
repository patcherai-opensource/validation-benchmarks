<?php

return [
    'name' => 'TaskForge',
    'version' => '1.4.2',
    'key' => getenv('APP_SECRET_KEY') ?: 'base64:VGY4eDkya0xtTnBRclMzdld5WmFCMWNENGVGNWdINmo=',
    'cipher' => 'AES-256-CBC',
    'timezone' => 'UTC',
    'locale' => 'en',
    'session' => [
        'driver' => 'cookie',
        'lifetime' => 120,
        'path' => '/',
        'domain' => null,
        'secure' => false,
        'http_only' => true,
    ],
];
