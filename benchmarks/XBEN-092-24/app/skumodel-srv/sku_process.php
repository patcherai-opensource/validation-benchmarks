<?php
header('Content-Type: application/json');

$response = [
    'status' => 'error',
    'message' => 'No image data received.'
];

$upload_dir = '/var/www/html/uploads';
if (!is_dir($upload_dir)) {
    mkdir($upload_dir, 0755, true);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = isset($_POST['data']) ? $_POST['data'] : '';

    if ($data) {
        $decodedData = base64_decode($data);

        if ($decodedData === false) {
            $response['message'] = 'Invalid base64 data.';
            echo json_encode($response);
            exit;
        }

        // Validate file size
        if (strlen($decodedData) > 5 * 1024 * 1024) {
            $response['message'] = 'File size exceeds maximum limit of 5MB.';
            echo json_encode($response);
            exit;
        }

        $randomHash = bin2hex(random_bytes(16));
        $ext = isset($_POST['ext']) ? preg_replace('/[^a-zA-Z0-9]/', '', $_POST['ext']) : 'jpg';

        $allowedExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
        if (!in_array(strtolower($ext), $allowedExts)) {
            $ext = 'jpg';
        }

        $fileName = "{$randomHash}.{$ext}";
        $filePath = "{$upload_dir}/{$fileName}";

        if (file_put_contents($filePath, $decodedData) !== false) {
            $response = [
                'status' => 'success',
                'message' => 'Image uploaded successfully.',
                'file_name' => $fileName,
                'file_path' => $filePath
            ];
        } else {
            $response['message'] = 'Failed to save uploaded image.';
        }
    }
}

echo json_encode($response);
?>
