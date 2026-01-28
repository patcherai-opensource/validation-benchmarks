<?php
header('Content-Type: application/json');
echo json_encode([
    'layers' => [
        ['id' => 1, 'name' => 'Global Administrative Boundaries', 'type' => 'vector', 'wms_url' => 'wms.openstreetmap.org/geoserver/admin_bounds/wms'],
        ['id' => 2, 'name' => 'OpenStreetMap Base', 'type' => 'raster', 'tile_url' => 'tile.openstreetmap.org/{z}/{x}/{y}.png'],
        ['id' => 3, 'name' => 'Satellite Imagery 2023', 'type' => 'raster'],
        ['id' => 4, 'name' => 'Elevation DEM', 'type' => 'raster'],
        ['id' => 5, 'name' => 'Climate Data', 'type' => 'vector'],
        ['id' => 6, 'name' => 'Population Density', 'type' => 'raster']
    ],
    'total' => 6,
    'page' => 1,
    'per_page' => 20
], JSON_PRETTY_PRINT);
?>
