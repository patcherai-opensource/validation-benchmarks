<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Location: /login.php');
    exit;
}

$username = $_SESSION['username'] ?? 'User';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Manager - Dashboard</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">MediaCMS</div>
        <div class="nav-links">
            <a href="/" class="active">Dashboard</a>
            <a href="/media.php">Media Library</a>
            <a href="/upload.php">Upload</a>
            <a href="/logout.php">Logout (<?php echo htmlspecialchars($username); ?>)</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="dashboard-header">
            <h1>Welcome to MediaCMS</h1>
            <p>Your content management system for media files</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Media Files</h3>
                <p class="stat-number"><?php 
                    $count = 0;
                    $media_dir = '/var/www/html/uploads/media/';
                    if (is_dir($media_dir)) {
                        $files = glob($media_dir . '*');
                        $count = count($files);
                    }
                    echo $count;
                ?></p>
            </div>
            <div class="stat-card">
                <h3>Quick Upload</h3>
                <p><a href="/upload.php" class="btn btn-primary">Upload New</a></p>
            </div>
            <div class="stat-card">
                <h3>Browse Library</h3>
                <p><a href="/media.php" class="btn btn-secondary">View All</a></p>
            </div>
        </div>
        
        <div class="recent-uploads">
            <h2>Recent Uploads</h2>
            <div class="media-grid">
                <?php
                if (is_dir($media_dir)) {
                    $files = glob($media_dir . '*.{jpg,jpeg,png,gif}', GLOB_BRACE);
                    $recent = array_slice($files, -6);
                    foreach ($recent as $file) {
                        $filename = basename($file);
                        echo '<div class="media-item">';
                        echo '<img src="/uploads/media/' . htmlspecialchars($filename) . '" alt="' . htmlspecialchars($filename) . '">';
                        echo '<span>' . htmlspecialchars($filename) . '</span>';
                        echo '</div>';
                    }
                }
                if (empty($recent)) {
                    echo '<p>No media files yet. <a href="/upload.php">Upload your first file</a>.</p>';
                }
                ?>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 MediaCMS. All rights reserved.</p>
    </footer>
</body>
</html>
