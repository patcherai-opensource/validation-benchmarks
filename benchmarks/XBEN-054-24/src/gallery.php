<?php
session_start();

// Get list of uploaded files
$uploadedFiles = [];
$uploadDir = '/var/www/html/uploads/';
if (is_dir($uploadDir)) {
    $files = scandir($uploadDir);
    foreach ($files as $file) {
        if ($file !== '.' && $file !== '..') {
            $ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));
            $uploadedFiles[] = [
                'name' => $file,
                'ext' => $ext,
                'isImage' => in_array($ext, ['jpg', 'jpeg', 'png', 'gif', 'webp'])
            ];
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gallery - MediaShare Pro</title>
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
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 2rem;
        }
        h1 {
            color: #00d4ff;
            margin-bottom: 2rem;
        }
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1.5rem;
        }
        .gallery-item {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s;
        }
        .gallery-item:hover {
            transform: scale(1.02);
        }
        .gallery-item img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }
        .gallery-item .file-icon {
            width: 100%;
            height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            background: rgba(0,0,0,0.3);
        }
        .gallery-item .file-name {
            padding: 1rem;
            font-size: 0.9rem;
            word-break: break-all;
        }
        .gallery-item a {
            color: #e0e0e0;
            text-decoration: none;
        }
        .empty-gallery {
            text-align: center;
            padding: 3rem;
            color: #666;
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
            <a href="/login.php">Login</a>
            <a href="/api/status.php">API</a>
        </div>
    </nav>
    
    <div class="container">
        <h1>Media Gallery</h1>
        
        <?php if (empty($uploadedFiles)): ?>
            <div class="empty-gallery">
                <p>No media files uploaded yet.</p>
                <p><a href="/upload.php" style="color: #00d4ff;">Upload your first file</a></p>
            </div>
        <?php else: ?>
            <div class="gallery-grid">
                <?php foreach ($uploadedFiles as $file): ?>
                    <div class="gallery-item">
                        <a href="/uploads/<?php echo htmlspecialchars($file['name']); ?>" target="_blank">
                            <?php if ($file['isImage']): ?>
                                <img src="/uploads/<?php echo htmlspecialchars($file['name']); ?>" alt="<?php echo htmlspecialchars($file['name']); ?>">
                            <?php else: ?>
                                <div class="file-icon">📄</div>
                            <?php endif; ?>
                            <div class="file-name"><?php echo htmlspecialchars($file['name']); ?></div>
                        </a>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
