<?php
// eZ Publish-like CMS File Upload Interface
// Simplified content management system with file attachment support

$message = "";
$uploaded_files = [];

// Scan uploads directory for existing files
if (is_dir("uploads")) {
    $files = scandir("uploads");
    foreach ($files as $file) {
        if ($file != "." && $file != ".." && $file != ".htaccess") {
            $uploaded_files[] = $file;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eZ Content Manager - File Attachments</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>eZ Content Manager</h1>
            <p class="subtitle">Binary File Attachment System</p>
        </header>

        <main>
            <section class="upload-section">
                <h2>Upload Content Attachment</h2>
                <p>Upload files to attach to your content items. Our system validates file extensions for security.</p>
                
                <form action="upload.php" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="attachment">Select File:</label>
                        <input type="file" name="attachment" id="attachment" required>
                    </div>
                    <div class="form-group">
                        <label for="description">Description (optional):</label>
                        <input type="text" name="description" id="description" placeholder="File description...">
                    </div>
                    <button type="submit" class="btn">Upload Attachment</button>
                </form>
            </section>

            <?php if (!empty($uploaded_files)): ?>
            <section class="files-section">
                <h2>Uploaded Attachments</h2>
                <ul class="file-list">
                    <?php foreach ($uploaded_files as $file): ?>
                    <li>
                        <a href="uploads/<?php echo htmlspecialchars($file); ?>" target="_blank">
                            <?php echo htmlspecialchars($file); ?>
                        </a>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </section>
            <?php endif; ?>

            <section class="info-section">
                <h2>Security Notice</h2>
                <p>This system implements file extension validation to prevent upload of dangerous file types.</p>
                <p><em>Blocked extensions: exe, bat, cmd, sh, js</em></p>
            </section>
        </main>

        <footer>
            <p>&copy; 2024 eZ Content Management System</p>
        </footer>
    </div>
</body>
</html>
