<?php
header('Content-Type: application/json');

$response = [
    'status' => 'failure',
    'message' => 'Invalid request.'
];

$filePath = isset($_POST['file_path']) ? $_POST['file_path'] : '';

if (!empty($filePath) && file_exists($filePath)) {
    $fileInfo = pathinfo($filePath);
    $response = [
        'status' => 'success',
        'message' => 'File found.',
        'file_info' => [
            'path' => $filePath,
            'extension' => isset($fileInfo['extension']) ? $fileInfo['extension'] : 'none',
            'size' => filesize($filePath)
        ]
    ];
} else {
    $response['message'] = 'File not found.';
}

echo json_encode($response);
?>
