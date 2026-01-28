<!DOCTYPE html>
<html>
<head>
    <title>MediaFlow CMS - Gallery</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5em; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .header nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .panel { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .panel h2 { color: #2c3e50; margin-bottom: 20px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .gallery-item { background: #f8f9fa; border-radius: 4px; padding: 10px; text-align: center; }
        .gallery-item img { max-width: 100%; height: 150px; object-fit: cover; border-radius: 4px; }
        .gallery-item p { margin-top: 10px; font-size: 0.9em; color: #7f8c8d; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9em; }
        .empty { text-align: center; color: #7f8c8d; padding: 40px; }
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
        <div class="panel">
            <h2>🖼️ Media Gallery</h2>
            <?php
            $upload_dir = '/var/www/html/upload/';
            $image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
            $files = [];
            
            if (is_dir($upload_dir)) {
                $items = scandir($upload_dir);
                foreach ($items as $item) {
                    if ($item !== '.' && $item !== '..' && is_file($upload_dir . $item)) {
                        $ext = strtolower(pathinfo($item, PATHINFO_EXTENSION));
                        if (in_array($ext, $image_extensions)) {
                            $files[] = $item;
                        }
                    }
                }
            }
            
            if (empty($files)):
            ?>
                <div class="empty">
                    <p>No images in gallery yet.</p>
                    <p>Upload images via the <a href="/admin/media.php">Media Manager</a></p>
                </div>
            <?php else: ?>
                <div class="gallery-grid">
                    <?php foreach ($files as $file): ?>
                        <div class="gallery-item">
                            <img src="/upload/<?= htmlspecialchars($file) ?>" alt="<?= htmlspecialchars($file) ?>">
                            <p><?= htmlspecialchars($file) ?></p>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
