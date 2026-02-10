<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Location: /login.php');
    exit;
}

$username = $_SESSION['username'] ?? 'User';
$media_dir = '/var/www/html/uploads/media/';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Library - MediaCMS</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">MediaCMS</div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/media.php" class="active">Media Library</a>
            <a href="/upload.php">Upload</a>
            <a href="/logout.php">Logout (<?php echo htmlspecialchars($username); ?>)</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h1>Media Library</h1>
            <a href="/upload.php" class="btn btn-primary">Upload New</a>
        </div>
        
        <div class="media-library">
            <?php
            if (is_dir($media_dir)) {
                $files = glob($media_dir . '*');
                if (!empty($files)) {
                    echo '<div class="media-grid large">';
                    foreach ($files as $file) {
                        if (is_file($file)) {
                            $filename = basename($file);
                            $ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
                            echo '<div class="media-item">';
                            if (in_array($ext, ['jpg', 'jpeg', 'png', 'gif', 'webp'])) {
                                echo '<img src="/uploads/media/' . htmlspecialchars($filename) . '" alt="' . htmlspecialchars($filename) . '">';
                            } else {
                                echo '<div class="file-icon">' . strtoupper($ext) . '</div>';
                            }
                            echo '<div class="media-info">';
                            echo '<span class="filename">' . htmlspecialchars($filename) . '</span>';
                            echo '<span class="filesize">' . round(filesize($file) / 1024, 2) . ' KB</span>';
                            echo '</div>';
                            echo '</div>';
                        }
                    }
                    echo '</div>';
                } else {
                    echo '<div class="empty-state">';
                    echo '<p>No media files found.</p>';
                    echo '<a href="/upload.php" class="btn btn-primary">Upload your first file</a>';
                    echo '</div>';
                }
            } else {
                echo '<div class="empty-state">';
                echo '<p>Media directory not initialized.</p>';
                echo '</div>';
            }
            ?>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 MediaCMS. All rights reserved.</p>
    </footer>
</body>
</html>
