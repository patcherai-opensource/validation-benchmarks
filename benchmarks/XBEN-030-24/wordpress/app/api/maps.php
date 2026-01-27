<?php
/**
 * GeoPortal Maps API
 */

header('Content-Type: application/json');

$maps = [
    'meta' => [
        'total_count' => 3,
        'page' => 1,
        'per_page' => 20
    ],
    'maps' => [
        [
            'id' => 1,
            'title' => 'World Overview',
            'abstract' => 'Global overview map with country boundaries.',
            'owner' => 'admin',
            'created_at' => '2024-01-15T10:30:00Z',
            'layers' => [1, 2]
        ],
        [
            'id' => 2,
            'title' => 'Terrain Analysis',
            'abstract' => 'Map for terrain and elevation analysis.',
            'owner' => 'geoanalyst',
            'created_at' => '2024-02-20T14:45:00Z',
            'layers' => [2, 3]
        ],
        [
            'id' => 3,
            'title' => 'Environmental Assessment',
            'abstract' => 'Land use and environmental data visualization.',
            'owner' => 'envteam',
            'created_at' => '2024-03-10T09:15:00Z',
            'layers' => [2, 4]
        ]
    ]
];

echo json_encode($maps, JSON_PRETTY_PRINT);
