<?php
header('Content-Type: application/json');
echo json_encode([
    'maps' => [
        ['id' => 101, 'title' => 'World Overview', 'owner' => 'admin', 'created' => '2024-01-15'],
        ['id' => 102, 'title' => 'Regional Analysis', 'owner' => 'analyst1', 'created' => '2024-02-20'],
        ['id' => 103, 'title' => 'Infrastructure Map', 'owner' => 'admin', 'created' => '2024-03-10']
    ],
    'total' => 3,
    'page' => 1
], JSON_PRETTY_PRINT);
?>
