<?php
header('Content-Type: application/json');
echo json_encode([
    'layers' => [
        ['id' => 1, 'name' => 'Global Administrative Boundaries', 'type' => 'vector', 'status' => 'active'],
        ['id' => 2, 'name' => 'OpenStreetMap Base', 'type' => 'raster', 'status' => 'active'],
        ['id' => 3, 'name' => 'Satellite Imagery 2023', 'type' => 'raster', 'status' => 'active'],
        ['id' => 4, 'name' => 'Elevation DEM', 'type' => 'raster', 'status' => 'active'],
        ['id' => 5, 'name' => 'Climate Data', 'type' => 'vector', 'status' => 'processing'],
        ['id' => 6, 'name' => 'Population Density', 'type' => 'raster', 'status' => 'active']
    ],
    'total' => 6,
    'page' => 1
], JSON_PRETTY_PRINT);
?>
