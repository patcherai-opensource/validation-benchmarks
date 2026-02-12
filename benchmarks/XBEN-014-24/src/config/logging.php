<?php

return [
    'default' => 'stack',
    'channels' => [
        'stack' => [
            'driver' => 'stack',
            'channels' => ['single'],
            'ignore_exceptions' => false,
        ],
        'single' => [
            'driver' => 'single',
            'path' => '/var/www/html/storage/logs/taskflow.log',
            'level' => 'debug',
        ],
    ],
];