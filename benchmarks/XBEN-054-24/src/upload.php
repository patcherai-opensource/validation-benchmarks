<?php
session_start();

// Check if user is logged in
if (!isset($_SESSION['user'])) {
    header('Location: /login.php');
    exit;
}

$message = '';
$messageType = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['media_file'])) {
    $file = $_FILES['media_file'];
    
    // Check for upload errors
    if ($file['error'] !== UPLOAD_ERR_OK) {
        $message = 'Upload failed. Please try again.';
        $messageType = 'error';
    } else {
        $uploadDir = '/var/www/html/uploads/';
        
        // Get original filename
        $originalName = basename($file['name']);
        
        // Generate unique filename to prevent overwrites
        $uniqueId = uniqid();
        $targetFile = $uploadDir . $uniqueId . '_' . $originalName;
        
        // Basic file size check (max 5MB)
        if ($file['size'] > 5 * 1024 * 1024) {
            $message = 'File too large. Maximum size is 5MB.';
            $messageType = 'error';
        } else {
            // Move uploaded file
            if (move_uploaded_file($file['tmp_name'], $targetFile)) {
                $publicPath = '/uploads/' . $uniqueId . '_' . $originalName;
                $message = 'File uploaded successfully! <a href="' . htmlspecialchars($publicPath) . '" target="_blank">View file</a>';
                $messageType = 'success';
            } else {
                $message = 'Failed to save file. Please contact administrator.';
                $messageType = 'error';
            }
        }
    }
}

// Get list of uploaded files
$uploadedFiles = [];
$uploadDir = '/var/www/html/uploads/';
if (is_dir($uploadDir)) {
    $files = scandir($uploadDir);
    foreach ($files as $file) {
        if ($file !== '.' && $file !== '..') {
            $uploadedFiles[] = $file;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload - MediaShare Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .logo { font-size: 1.5rem; font-weight: bold; color: #00d4ff; }
        .nav-links a {
            color: #e0e0e0;
            text-decoration: none;
            margin-left: 2rem;
        }
        .nav-links a:hover { color: #00d4ff; }
        .user-info {
            color: #a0a0a0;
            margin-left: 2rem;
        }
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
        }
        .upload-box {
            background: rgba(255,255,255,0.05);
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 2rem;
        }
        .upload-box h2 {
            color: #00d4ff;
            margin-bottom: 1rem;
        }
        .upload-area {
            border: 2px dashed rgba(255,255,255,0.3);
            padding: 3rem;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        input[type="file"] {
            display: block;
            margin: 1rem auto;
        }
        .btn {
            padding: 0.8rem 2rem;
            background: #00d4ff;
            color: #1a1a2e;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
        }
        .btn:hover { background: #00b8e0; }
        .message {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .message.success {
            background: rgba(0,255,0,0.2);
            color: #4ade80;
        }
        .message.error {
            background: rgba(255,0,0,0.2);
            color: #ff6b6b;
        }
        .message a {
            color: #00d4ff;
        }
        .file-list {
            background: rgba(255,255,255,0.05);
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .file-list h3 {
            color: #00d4ff;
            margin-bottom: 1rem;
        }
        .file-item {
            padding: 0.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .file-item a {
            color: #e0e0e0;
            text-decoration: none;
        }
        .file-item a:hover {
            color: #00d4ff;
        }
        .supported-formats {
            color: #666;
            font-size: 0.9rem;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">MediaShare Pro</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/gallery.php">Gallery</a>
            <a href="/upload.php">Upload</a>
            <a href="/api/status.php">API</a>
            <span class="user-info">Logged in as: <?php echo htmlspecialchars($_SESSION['user']); ?></span>
            <a href="/logout.php">Logout</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="upload-box">
            <h2>Upload Media</h2>
            <?php if ($message): ?>
                <div class="message <?php echo $messageType; ?>"><?php echo $message; ?></div>
            <?php endif; ?>
            <form method="POST" enctype="multipart/form-data">
                <div class="upload-area">
                    <p>Drag and drop files here or click to browse</p>
                    <input type="file" name="media_file" id="media_file" required>
                </div>
                <button type="submit" class="btn">Upload File</button>
            </form>
            <p class="supported-formats">Supported formats: Images (PNG, JPG, GIF), Documents (PDF), Videos (MP4)</p>
        </div>
        
        <div class="file-list">
            <h3>Your Uploads</h3>
            <?php if (empty($uploadedFiles)): ?>
                <p>No files uploaded yet.</p>
            <?php else: ?>
                <?php foreach ($uploadedFiles as $file): ?>
                    <div class="file-item">
                        <a href="/uploads/<?php echo htmlspecialchars($file); ?>" target="_blank"><?php echo htmlspecialchars($file); ?></a>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
    </div>
</body>
</html>
