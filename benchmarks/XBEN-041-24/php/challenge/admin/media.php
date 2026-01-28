<?php
session_start();

// Simple authentication check
function isLoggedIn() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}

// Handle login
if (isset($_POST['username']) && isset($_POST['password'])) {
    // Admin credentials (simple auth for this CMS)
    if ($_POST['username'] === 'admin' && $_POST['password'] === 'mediaflow2024') {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = 'admin';
    } else {
        $login_error = "Invalid credentials";
    }
}

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: /admin/media.php');
    exit;
}

// Allowed file extensions configuration (configurable like Automad)
// Note: This list is loaded from config - see ALLOWED_TYPES in config file
$ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico', 'php'];

// File type validation function - checks extension only (vulnerable like CVE-2024-40400)
function isAllowedFileType($filename, $allowed) {
    $ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
    return in_array($ext, $allowed);
}

// Handle file upload (only for authenticated admins)
$upload_message = '';
$upload_success = false;
if (isLoggedIn() && isset($_FILES['mediafile']) && $_FILES['mediafile']['error'] === UPLOAD_ERR_OK) {
    $upload_dir = '/var/www/html/upload/';
    $filename = basename($_FILES['mediafile']['name']);
    
    // Check if extension is allowed
    if (isAllowedFileType($filename, $ALLOWED_EXTENSIONS)) {
        $target_path = $upload_dir . $filename;
        
        if (move_uploaded_file($_FILES['mediafile']['tmp_name'], $target_path)) {
            $upload_message = "File uploaded successfully!";
            $upload_success = true;
        } else {
            $upload_message = "Error: Failed to move uploaded file.";
        }
    } else {
        $upload_message = "Error: File type not allowed. Permitted extensions: " . implode(', ', $ALLOWED_EXTENSIONS);
    }
}

// Get uploaded files
function getUploadedFiles($dir) {
    $files = [];
    if (is_dir($dir)) {
        $items = scandir($dir);
        foreach ($items as $item) {
            if ($item !== '.' && $item !== '..' && is_file($dir . $item)) {
                $files[] = $item;
            }
        }
    }
    return $files;
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>MediaFlow CMS - Media Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5em; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .header nav a:hover { text-decoration: underline; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .panel { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .panel h2 { color: #2c3e50; margin-bottom: 20px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #34495e; }
        .form-group input[type="text"], .form-group input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .form-group input[type="file"] { padding: 10px 0; }
        .btn { background: #3498db; color: white; padding: 12px 25px; border: none; border-radius: 4px; cursor: pointer; font-size: 1em; }
        .btn:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .message { padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .file-list { list-style: none; }
        .file-list li { padding: 10px 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .file-list li:hover { background: #f8f9fa; }
        .file-list a { color: #3498db; text-decoration: none; }
        .file-list a:hover { text-decoration: underline; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9em; }
        .user-info { background: #ecf0f1; padding: 10px 15px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📁 MediaFlow CMS</h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/pages.php">Pages</a>
            <a href="/admin/media.php">Media</a>
            <a href="/settings.php">Settings</a>
            <a href="/docs.php">Documentation</a>
        </nav>
    </div>
    <div class="container">
        <?php if (!isLoggedIn()): ?>
            <div class="panel">
                <h2>🔐 Admin Login Required</h2>
                <p style="margin-bottom: 20px;">You must be logged in as an administrator to access the media manager.</p>
                
                <?php if (isset($login_error)): ?>
                    <div class="message error"><?= htmlspecialchars($login_error) ?></div>
                <?php endif; ?>
                
                <form method="POST" action="">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">Login</button>
                </form>
            </div>
        <?php else: ?>
            <div class="user-info">
                <span>👤 Logged in as: <strong><?= htmlspecialchars($_SESSION['username']) ?></strong></span>
                <a href="?logout=1" class="btn btn-danger" style="padding: 8px 15px; text-decoration: none;">Logout</a>
            </div>
            
            <div class="panel">
                <h2>📤 Upload Media</h2>
                
                <?php if ($upload_message): ?>
                    <div class="message <?= $upload_success ? 'success' : 'error' ?>"><?= htmlspecialchars($upload_message) ?></div>
                <?php endif; ?>
                
                <form method="POST" action="" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="mediafile">Select File</label>
                        <input type="file" id="mediafile" name="mediafile" required>
                        <small style="color: #7f8c8d;">Allowed types: jpg, jpeg, png, gif, webp, svg, bmp, ico + configured types</small>
                    </div>
                    <button type="submit" class="btn">Upload File</button>
                </form>
            </div>
            
            <div class="panel">
                <h2>📁 Uploaded Files</h2>
                <?php 
                $files = getUploadedFiles('/var/www/html/upload/');
                if (empty($files)): ?>
                    <p style="color: #7f8c8d;">No files uploaded yet.</p>
                <?php else: ?>
                    <ul class="file-list">
                        <?php foreach ($files as $file): ?>
                            <li>
                                <a href="/upload/<?= htmlspecialchars($file) ?>" target="_blank"><?= htmlspecialchars($file) ?></a>
                                <span style="color: #95a5a6; font-size: 0.9em;"><?= date('Y-m-d H:i', filemtime('/var/www/html/upload/' . $file)) ?></span>
                            </li>
                        <?php endforeach; ?>
                    </ul>
                <?php endif; ?>
            </div>
        <?php endif; ?>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
