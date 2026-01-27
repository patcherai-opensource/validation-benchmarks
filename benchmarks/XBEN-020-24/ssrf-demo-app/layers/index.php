<?php
header('Content-Type: application/json');

echo json_encode(array(
    'layers' => array(
        array('id' => 'boundaries', 'name' => 'Administrative Boundaries', 'type' => 'vector'),
        array('id' => 'terrain', 'name' => 'Terrain Data', 'type' => 'raster'),
        array('id' => 'climate', 'name' => 'Climate Zones', 'type' => 'vector')
    )
), JSON_PRETTY_PRINT);
?>
