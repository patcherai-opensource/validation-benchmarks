<?php
header('Content-Type: application/json');

$response = array(
    'version' => '3.4.8',
    'build' => '2024-03-21T14:15:00Z',
    'title' => 'Reposilite',
    'status' => 'ALIVE',
    'authenticated' => false,
    'basePath' => '/',
    'id' => 'reposilite-prod-01',
    'repositories' => array(
        array('name' => 'releases', 'visibility' => 'PUBLIC'),
        array('name' => 'snapshots', 'visibility' => 'PUBLIC'),
        array('name' => 'public', 'visibility' => 'PUBLIC')
    ),
    'uptime' => time() - (int)(time() / 86400) * 86400,
    'memoryUsed' => memory_get_usage(true),
    'memoryMax' => 536870912
);

echo json_encode($response, JSON_PRETTY_PRINT);
exit;
