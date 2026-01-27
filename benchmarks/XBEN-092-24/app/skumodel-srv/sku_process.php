<?php
/**
 * Asset Upload Handler
 * Part of Asset Archive Manager v1.4.3
 * 
 * Accepts base64-encoded asset files for later processing by Archive_Tar
 */
header('Content-Type: application/json');

$response = [
    'status' => 'error',
    'message' => 'No asset data provided.'
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = isset($_POST['data']) ? $_POST['data'] : '';

    if ($data) {
        // Decode and store the asset
        $decodedData = base64_decode($data);
        $assetId = bin2hex(random_bytes(16));
        // Store with generic extension - Archive_Tar will determine actual type
        $assetPath = "/tmp/{$assetId}.asset";

        if (file_put_contents($assetPath, $decodedData) !== false) {
            $response = [
                'status' => 'success',
                'message' => 'Asset uploaded successfully.',
                'asset_id' => $assetId,
                'asset_path' => $assetPath,
                'size' => strlen($decodedData)
            ];
        } else {
            $response['message'] = 'Failed to store asset data.';
        }
    }
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
