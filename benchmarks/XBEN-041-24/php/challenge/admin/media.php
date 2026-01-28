<?php
session_start();

// Check authentication
if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header("Location: /admin/");
    exit;
}

$upload_dir = "/var/www/html/upload/";
$message = "";
$message_type = "";

// Handle file upload
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['mediafile'])) {
    $file = $_FILES['mediafile'];
    
    if ($file['error'] === UPLOAD_ERR_OK) {
        // Get the file extension
        $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        
        // Only allow image extensions (but this is easily bypassed)
        $allowed = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
        
        if (in_array($ext, $allowed)) {
            $filename = basename($file['name']);
            $target = $upload_dir . $filename;
            
            if (move_uploaded_file($file['tmp_name'], $target)) {
                $message = "File uploaded successfully to /upload/" . htmlspecialchars($filename);
                $message_type = "success";
            } else {
                $message = "Error moving uploaded file.";
                $message_type = "error";
            }
        } else {
            $message = "Error: Only image files (jpg, jpeg, png, gif, webp) are allowed.";
            $message_type = "error";
        }
    } else {
        $message = "Upload error: " . $file['error'];
        $message_type = "error";
    }
}

// Get list of uploaded files
$files = [];
if (is_dir($upload_dir)) {
    $items = scandir($upload_dir);
    foreach ($items as $item) {
        if ($item !== '.' && $item !== '..') {
            $files[] = $item;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Manager - Aimeos CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .navbar { background: #2c3e50; padding: 15px 30px; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .breadcrumb { color: #7f8c8d; margin-bottom: 20px; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .card { background: white; border-radius: 8px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .card h2 { color: #2c3e50; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        .form-group input[type="file"] { padding: 10px; border: 2px dashed #ddd; border-radius: 5px; width: 100%; cursor: pointer; }
        .btn { padding: 12px 25px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }
        .btn:hover { background: #2980b9; }
        .message { padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .file-list { list-style: none; }
        .file-list li { padding: 10px 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .file-list li:last-child { border-bottom: none; }
        .file-list a { color: #3498db; text-decoration: none; }
        .note { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin-top: 20px; color: #856404; }
        .note strong { display: block; margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🎨 Aimeos CMS - Media Manager</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/docs/">Documentation</a>
        </nav>
    </div>
    
    <div class="container">
        <div class="breadcrumb">
            <a href="/admin/">Dashboard</a> / Media Manager
        </div>
        
        <?php if ($message): ?>
        <div class="message <?php echo $message_type; ?>">
            <?php echo $message; ?>
        </div>
        <?php endif; ?>
        
        <div class="card">
            <h2>📤 Upload Media</h2>
            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="mediafile">Select Image File</label>
                    <input type="file" id="mediafile" name="mediafile" accept="image/*" required>
                </div>
                <button type="submit" class="btn">Upload File</button>
            </form>
            
            <div class="note">
                <strong>ℹ️ Note:</strong>
                This basic upload interface only accepts image files. For advanced upload options including custom paths, use the <a href="/api/media">Media API</a>.
            </div>
        </div>
        
        <div class="card">
            <h2>📁 Uploaded Files</h2>
            <?php if (empty($files)): ?>
            <p style="color: #7f8c8d;">No files uploaded yet.</p>
            <?php else: ?>
            <ul class="file-list">
                <?php foreach ($files as $file): ?>
                <li>
                    <a href="/upload/<?php echo htmlspecialchars($file); ?>" target="_blank">
                        <?php echo htmlspecialchars($file); ?>
                    </a>
                </li>
                <?php endforeach; ?>
            </ul>
            <?php endif; ?>
        </div>
    </div>
</body>
</html>
