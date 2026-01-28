<?php
header('Content-Type: application/json');

// Read experiments from storage
$json_data = file_get_contents('../../../../experiments.json');
$experiments = json_decode($json_data, true);

$response = [
    'experiments' => array_map(function($exp) {
        return [
            'experiment_id' => $exp['id'],
            'name' => $exp['name'],
            'artifact_location' => $exp['artifact_location'],
            'lifecycle_stage' => 'active',
            'last_update_time' => time() - rand(3600, 86400)
        ];
    }, $experiments)
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
