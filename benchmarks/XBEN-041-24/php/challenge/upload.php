<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Location: /login.php');
    exit;
}

$username = $_SESSION['username'] ?? 'User';
$message = '';
$message_type = '';

$allowed_mime_types = [
    'image/jpeg',
    'image/png', 
    'image/gif',
    'image/webp',
    'application/pdf',
    'text/plain'
];

function isAllowed($mime) {
    global $allowed_mime_types;
    return in_array($mime, $allowed_mime_types);
}

function generatePath($filename, $mime, $domain = 'media') {
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    $hash = substr(md5(uniqid()), 0, 12);
    return "uploads/{$domain}/{$hash}.{$ext}";
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['mediafile'])) {
    $file = $_FILES['mediafile'];
    
    if ($file['error'] === UPLOAD_ERR_OK) {
        $finfo = new finfo(FILEINFO_MIME_TYPE);
        $mime = $finfo->file($file['tmp_name']);
        
        if (isAllowed($mime)) {
            $media_url = $_POST['media_url'] ?? '';
            
            if (!empty($media_url)) {
                $path = $media_url;
            } else {
                $path = generatePath($file['name'], $mime);
            }
            
            $full_path = '/var/www/html/' . $path;
            
            $dir = dirname($full_path);
            if (!is_dir($dir)) {
                mkdir($dir, 0755, true);
            }
            
            $content = file_get_contents($file['tmp_name']);
            
            if (file_put_contents($full_path, $content) !== false) {
                $message = "File uploaded successfully to: /{$path}";
                $message_type = 'success';
            } else {
                $message = "Failed to save file";
                $message_type = 'error';
            }
        } else {
            $message = "File type not allowed. Allowed types: JPEG, PNG, GIF, WebP, PDF, TXT";
            $message_type = 'error';
        }
    } else {
        $message = "Upload error occurred";
        $message_type = 'error';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Media - MediaCMS</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">MediaCMS</div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/media.php">Media Library</a>
            <a href="/upload.php" class="active">Upload</a>
            <a href="/logout.php">Logout (<?php echo htmlspecialchars($username); ?>)</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h1>Upload Media</h1>
        </div>
        
        <?php if ($message): ?>
            <div class="alert alert-<?php echo $message_type; ?>">
                <?php echo htmlspecialchars($message); ?>
            </div>
        <?php endif; ?>
        
        <div class="upload-form-container">
            <form method="POST" enctype="multipart/form-data" class="upload-form">
                <div class="form-group">
                    <label for="mediafile">Select File</label>
                    <input type="file" id="mediafile" name="mediafile" required>
                    <small>Allowed: JPEG, PNG, GIF, WebP, PDF, TXT (Max 10MB)</small>
                </div>
                
                <div class="form-group">
                    <label for="media_url">Custom Path (Optional)</label>
                    <input type="text" id="media_url" name="media_url" placeholder="e.g., uploads/media/custom-name.jpg">
                    <small>Leave empty for auto-generated path. Advanced users can specify custom storage path.</small>
                </div>
                
                <button type="submit" class="btn btn-primary">Upload File</button>
            </form>
        </div>
        
        <div class="upload-info">
            <h3>Upload Guidelines</h3>
            <ul>
                <li>Maximum file size: 10MB</li>
                <li>Supported formats: Images (JPEG, PNG, GIF, WebP), Documents (PDF, TXT)</li>
                <li>Files are stored in the media library for easy access</li>
            </ul>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 MediaCMS. All rights reserved.</p>
    </footer>
</body>
</html>
