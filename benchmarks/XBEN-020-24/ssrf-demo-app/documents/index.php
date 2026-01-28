<?php
header('Content-Type: application/json');
echo json_encode([
    'documents' => [
        ['id' => 201, 'title' => 'GIS Analysis Report Q1', 'type' => 'pdf', 'size' => '2.4MB'],
        ['id' => 202, 'title' => 'Satellite Data Processing Guide', 'type' => 'pdf', 'size' => '1.1MB'],
        ['id' => 203, 'title' => 'Layer Metadata Standards', 'type' => 'docx', 'size' => '456KB']
    ],
    'total' => 3,
    'page' => 1
], JSON_PRETTY_PRINT);
?>
