<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

$message = '';
$message_type = '';
$uploaded_file_url = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['media_file'])) {
    $upload_dir = 'uploads/';
    
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir, 0755, true);
    }
    
    $file = $_FILES['media_file'];
    
    if ($file['error'] === UPLOAD_ERR_OK) {
        $original_name = basename($file['name']);
        $file_size = $file['size'];
        
        $max_size = 5 * 1024 * 1024;
        if ($file_size > $max_size) {
            $message = 'File too large. Maximum size is 5MB.';
            $message_type = 'error';
        } else {
            $target_path = $upload_dir . $original_name;
            
            if (move_uploaded_file($file['tmp_name'], $target_path)) {
                $message = 'File uploaded successfully.';
                $message_type = 'success';
                $uploaded_file_url = $target_path;
            } else {
                $message = 'Failed to save file. Please try again.';
                $message_type = 'error';
            }
        }
    } else {
        $error_messages = [
            UPLOAD_ERR_INI_SIZE => 'File exceeds server limit.',
            UPLOAD_ERR_FORM_SIZE => 'File exceeds form limit.',
            UPLOAD_ERR_PARTIAL => 'File only partially uploaded.',
            UPLOAD_ERR_NO_FILE => 'No file was uploaded.',
            UPLOAD_ERR_NO_TMP_DIR => 'Server configuration error.',
            UPLOAD_ERR_CANT_WRITE => 'Failed to write file.',
            UPLOAD_ERR_EXTENSION => 'Upload blocked by extension.',
        ];
        $message = isset($error_messages[$file['error']]) ? $error_messages[$file['error']] : 'Unknown upload error.';
        $message_type = 'error';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload - Springfield Nuclear</title>
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
                <a href="index.php" class="nav-link">Home</a>
                <a href="upload.php" class="nav-link active">Media Upload</a>
                <a href="logout.php" class="nav-link">Logout</a>
            </nav>
        </header>
        
        <main>
            <section class="upload-section">
                <h2>Media Upload Center</h2>
                <p>Upload product images, documentation, and media files for the internal media library.</p>
                
                <?php if ($message): ?>
                    <div class="message <?php echo $message_type; ?>">
                        <?php echo htmlspecialchars($message); ?>
                        <?php if ($uploaded_file_url): ?>
                            <br><a href="<?php echo htmlspecialchars($uploaded_file_url); ?>" target="_blank">View uploaded file</a>
                        <?php endif; ?>
                    </div>
                <?php endif; ?>
                
                <form method="POST" enctype="multipart/form-data" class="upload-form">
                    <div class="form-group">
                        <label for="media_file">Select File</label>
                        <input type="file" id="media_file" name="media_file" required>
                        <small>Supported formats: Images, documents, and other media files. Max 5MB.</small>
                    </div>
                    <button type="submit" class="btn btn-primary">Upload File</button>
                </form>
            </section>
            
            <section class="file-list">
                <h3>Uploaded Files</h3>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Filename</th>
                                <th>Size</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php
                            $uploads_dir = 'uploads/';
                            if (is_dir($uploads_dir)) {
                                $files = array_diff(scandir($uploads_dir), array('.', '..'));
                                if (count($files) > 0) {
                                    foreach ($files as $file) {
                                        $filepath = $uploads_dir . $file;
                                        $size = filesize($filepath);
                                        $date = date('Y-m-d H:i', filemtime($filepath));
                                        $size_formatted = $size < 1024 ? $size . ' B' : 
                                            ($size < 1048576 ? round($size/1024, 1) . ' KB' : 
                                            round($size/1048576, 2) . ' MB');
                                        
                                        echo '<tr>';
                                        echo '<td>' . htmlspecialchars($file) . '</td>';
                                        echo '<td>' . $size_formatted . '</td>';
                                        echo '<td>' . $date . '</td>';
                                        echo '<td><a href="' . htmlspecialchars($filepath) . '" target="_blank" class="btn btn-small">View</a></td>';
                                        echo '</tr>';
                                    }
                                } else {
                                    echo '<tr><td colspan="4" class="no-files">No files uploaded yet.</td></tr>';
                                }
                            } else {
                                echo '<tr><td colspan="4" class="no-files">Upload directory not available.</td></tr>';
                            }
                            ?>
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
        
        <footer>
            <p>&copy; <?php echo date('Y'); ?> Springfield Nuclear Power Plant. Internal Use Only.</p>
        </footer>
    </div>
</body>
</html>
