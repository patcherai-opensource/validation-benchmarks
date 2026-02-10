<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Location: login.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Springfield Nuclear - Media Portal</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <img src="static/homer_simpson.png" alt="Logo" class="logo-img">
                <h1>Springfield Nuclear Power Plant</h1>
            </div>
            <nav>
                <a href="index.php" class="nav-link active">Home</a>
                <a href="upload.php" class="nav-link">Media Upload</a>
                <a href="logout.php" class="nav-link">Logout</a>
            </nav>
        </header>
        
        <main>
            <section class="welcome-section">
                <h2>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
                <p>You are logged into the Springfield Nuclear Power Plant Media Portal.</p>
            </section>
            
            <section class="features">
                <div class="feature-card">
                    <h3>Media Library</h3>
                    <p>Browse and manage your uploaded media files.</p>
                </div>
                <div class="feature-card">
                    <h3>Upload Center</h3>
                    <p>Upload product images and documentation.</p>
                    <a href="upload.php" class="btn">Go to Upload</a>
                </div>
                <div class="feature-card">
                    <h3>Recent Activity</h3>
                    <p>View your recent uploads and modifications.</p>
                </div>
            </section>
            
            <section class="uploads-preview">
                <h3>Recent Uploads</h3>
                <div class="upload-grid">
                    <?php
                    $uploads_dir = 'uploads/';
                    if (is_dir($uploads_dir)) {
                        $files = array_diff(scandir($uploads_dir), array('.', '..'));
                        $count = 0;
                        foreach ($files as $file) {
                            if ($count >= 6) break;
                            $ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));
                            echo '<div class="upload-item">';
                            if (in_array($ext, ['jpg', 'jpeg', 'png', 'gif'])) {
                                echo '<img src="uploads/' . htmlspecialchars($file) . '" alt="' . htmlspecialchars($file) . '">';
                            } else {
                                echo '<div class="file-icon">' . strtoupper($ext) . '</div>';
                            }
                            echo '<span>' . htmlspecialchars($file) . '</span>';
                            echo '</div>';
                            $count++;
                        }
                        if ($count === 0) {
                            echo '<p class="no-uploads">No files uploaded yet.</p>';
                        }
                    } else {
                        echo '<p class="no-uploads">Upload directory not available.</p>';
                    }
                    ?>
                </div>
            </section>
        </main>
        
        <footer>
            <p>&copy; <?php echo date('Y'); ?> Springfield Nuclear Power Plant. Internal Use Only.</p>
        </footer>
    </div>
</body>
</html>
