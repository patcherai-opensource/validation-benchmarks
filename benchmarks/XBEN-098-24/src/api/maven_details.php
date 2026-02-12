<?php
header('Content-Type: application/json');

$path = isset($m[1]) ? ltrim($m[1], '/') : '';

$details = [
    'type' => 'DIRECTORY',
    'files' => [
        ['name' => 'releases', 'type' => 'DIRECTORY', 'contentLength' => 0],
        ['name' => 'snapshots', 'type' => 'DIRECTORY', 'contentLength' => 0],
    ]
];

if ($path === 'releases') {
    $details = [
        'type' => 'DIRECTORY',
        'files' => [
            ['name' => 'com', 'type' => 'DIRECTORY', 'contentLength' => 0],
            ['name' => 'org', 'type' => 'DIRECTORY', 'contentLength' => 0],
            ['name' => 'io', 'type' => 'DIRECTORY', 'contentLength' => 0],
        ]
    ];
} elseif ($path === 'snapshots') {
    $details = [
        'type' => 'DIRECTORY',
        'files' => [
            ['name' => 'com', 'type' => 'DIRECTORY', 'contentLength' => 0],
            ['name' => 'org', 'type' => 'DIRECTORY', 'contentLength' => 0],
        ]
    ];
}

echo json_encode($details);
exit;
