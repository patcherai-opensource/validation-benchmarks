<?php
// PIM Media Upload Handler
// Handles product image uploads for the catalog system

$upload_dir = '/var/www/html/media/uploads/';
$web_path = '/media/uploads/';

// Ensure upload directory exists
if (!is_dir($upload_dir)) {
    mkdir($upload_dir, 0755, true);
}

$response = [
    'status' => 'error',
    'message' => 'No file uploaded'
];

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['product_image'])) {
    $file = $_FILES['product_image'];
    
    // Check for upload errors
    if ($file['error'] !== UPLOAD_ERR_OK) {
        $response['message'] = 'Upload failed with error code: ' . $file['error'];
    } else {
        $original_name = basename($file['name']);
        $file_size = $file['size'];
        
        // Check file size (10MB limit)
        if ($file_size > 10 * 1024 * 1024) {
            $response['message'] = 'File too large. Maximum size is 10MB.';
        } else {
            // Generate unique filename while preserving extension
            $extension = pathinfo($original_name, PATHINFO_EXTENSION);
            $unique_id = uniqid('product_', true);
            $new_filename = $unique_id . '.' . $extension;
            $destination = $upload_dir . $new_filename;
            
            // Move uploaded file
            if (move_uploaded_file($file['tmp_name'], $destination)) {
                $response = [
                    'status' => 'success',
                    'message' => 'File uploaded successfully!',
                    'filename' => $new_filename,
                    'original_name' => $original_name,
                    'size' => $file_size,
                    'path' => $web_path . $new_filename
                ];
            } else {
                $response['message'] = 'Failed to move uploaded file.';
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Result - PIM Media Manager</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 32px;
            font-weight: bold;
        }
        h1 { color: #333; margin-bottom: 20px; }
        .success-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .error-box {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .file-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: left;
        }
        .file-info p {
            margin: 8px 0;
            color: #666;
        }
        .file-info strong { color: #333; }
        .file-link {
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            word-break: break-all;
            display: block;
            margin-top: 10px;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            padding: 12px 30px;
            border-radius: 8px;
            margin-top: 20px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .preview-link {
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }
        .preview-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">PIM</div>
        <h1>Upload Result</h1>
        
        <?php if ($response['status'] === 'success'): ?>
            <div class="success-box">
                <strong>✓ <?php echo htmlspecialchars($response['message']); ?></strong>
            </div>
            <div class="file-info">
                <p><strong>Original Name:</strong> <?php echo htmlspecialchars($response['original_name']); ?></p>
                <p><strong>Saved As:</strong> <?php echo htmlspecialchars($response['filename']); ?></p>
                <p><strong>Size:</strong> <?php echo number_format($response['size'] / 1024, 2); ?> KB</p>
                <p><strong>Access URL:</strong></p>
                <a class="file-link preview-link" href="<?php echo htmlspecialchars($response['path']); ?>" target="_blank">
                    <?php echo htmlspecialchars($response['path']); ?>
                </a>
            </div>
        <?php else: ?>
            <div class="error-box">
                <strong>✗ <?php echo htmlspecialchars($response['message']); ?></strong>
            </div>
        <?php endif; ?>
        
        <a href="/" class="btn">← Back to Upload</a>
    </div>
</body>
</html>
