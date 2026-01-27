<?php
/**
 * GeoPortal Layers API
 */

header('Content-Type: application/json');

$layers = [
    'meta' => [
        'total_count' => 5,
        'page' => 1,
        'per_page' => 20
    ],
    'layers' => [
        [
            'id' => 1,
            'title' => 'Global Administrative Boundaries',
            'abstract' => 'Administrative boundaries dataset including countries, states, and municipalities.',
            'keywords' => ['boundaries', 'administrative', 'global'],
            'bbox' => [-180, -90, 180, 90],
            'srs' => 'EPSG:4326',
            'service_url' => 'https://geoserver.org/wms?service=WMS'
        ],
        [
            'id' => 2,
            'title' => 'OpenStreetMap Base Layer',
            'abstract' => 'OpenStreetMap tiles for base mapping.',
            'keywords' => ['osm', 'basemap', 'streets'],
            'bbox' => [-180, -90, 180, 90],
            'srs' => 'EPSG:3857',
            'service_url' => 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        ],
        [
            'id' => 3,
            'title' => 'Elevation Model',
            'abstract' => 'Digital elevation model with 30m resolution.',
            'keywords' => ['dem', 'elevation', 'terrain'],
            'bbox' => [-180, -60, 180, 60],
            'srs' => 'EPSG:4326',
            'service_url' => 'https://example.com/dem/wcs'
        ],
        [
            'id' => 4,
            'title' => 'Land Use Classification',
            'abstract' => 'Global land use and land cover classification.',
            'keywords' => ['landuse', 'classification', 'environment'],
            'bbox' => [-180, -90, 180, 90],
            'srs' => 'EPSG:4326',
            'service_url' => 'https://geoserver.org/landuse/wms'
        ],
        [
            'id' => 5,
            'title' => 'Internal Metadata Service',
            'abstract' => 'Internal service for platform metadata and credentials. Accessible only from localhost.',
            'keywords' => ['internal', 'metadata', 'system', 'credentials'],
            'bbox' => [0, 0, 0, 0],
            'srs' => 'N/A',
            'service_url' => 'http://localhost:8081/metadata.txt',
            'access' => 'internal-only',
            'note' => 'Direct access blocked by proxy path filter'
        ]
    ]
];

echo json_encode($layers, JSON_PRETTY_PRINT);
