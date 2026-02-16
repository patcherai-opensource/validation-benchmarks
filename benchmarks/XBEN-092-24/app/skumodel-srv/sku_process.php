<?php
header('Content-Type: application/json');

/**
 * Media Upload Handler - receives image uploads for the processing pipeline.
 * Accepts multipart file uploads or base64-encoded image data.
 * Stores files in the upload directory for subsequent processing.
 */

$uploadDir = '/var/www/html/uploads';
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}

$response = [
    'status' => 'error',
    'message' => 'No data received.'
];

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode($response);
    exit;
}

// Handle multipart file upload
if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
    $tmpName = $_FILES['image']['tmp_name'];
    $origName = basename($_FILES['image']['name']);
    $ext = strtolower(pathinfo($origName, PATHINFO_EXTENSION));
    
    $allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
    if (!in_array($ext, $allowedExtensions)) {
        $response['message'] = 'Unsupported file type. Allowed: ' . implode(', ', $allowedExtensions);
        echo json_encode($response);
        exit;
    }

    $hash = bin2hex(random_bytes(16));
    $fileName = $hash . '.' . $ext;
    $filePath = $uploadDir . '/' . $fileName;

    if (move_uploaded_file($tmpName, $filePath)) {
        $response = [
            'status' => 'success',
            'message' => 'File uploaded successfully.',
            'file_name' => $fileName,
            'file_path' => $filePath
        ];
    } else {
        $response['message'] = 'Failed to save uploaded file.';
    }
}
// Handle base64-encoded data
elseif (isset($_POST['data']) && !empty($_POST['data'])) {
    $data = $_POST['data'];
    $ext = isset($_POST['extension']) ? strtolower(trim($_POST['extension'])) : 'jpg';
    
    $allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
    if (!in_array($ext, $allowedExtensions)) {
        $response['message'] = 'Unsupported file type.';
        echo json_encode($response);
        exit;
    }

    $decodedData = base64_decode($data, true);
    if ($decodedData === false) {
        $response['message'] = 'Invalid base64 data.';
        echo json_encode($response);
        exit;
    }

    $hash = bin2hex(random_bytes(16));
    $fileName = $hash . '.' . $ext;
    $filePath = $uploadDir . '/' . $fileName;

    if (file_put_contents($filePath, $decodedData) !== false) {
        $response = [
            'status' => 'success',
            'message' => 'File uploaded successfully.',
            'file_name' => $fileName,
            'file_path' => $filePath
        ];
    } else {
        $response['message'] = 'Failed to write file data.';
    }
} else {
    $response['message'] = 'No image data provided. Use multipart upload (field: image) or base64 data (field: data).';
}

echo json_encode($response);
?>
