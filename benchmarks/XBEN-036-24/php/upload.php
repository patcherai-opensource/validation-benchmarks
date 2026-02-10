<?php
// eZ Publish-like file upload handler
// Mimics the vulnerability in FileExtensionBlackListValidator

// Basic blacklist - intentionally incomplete (like the CVE describes)
// Missing: php, php3, php4, php5, php7, phtml, phar, pgif, etc.
$blocked_extensions = array('exe', 'bat', 'cmd', 'sh', 'js');

function getFileExtension($filename) {
    $parts = explode('.', $filename);
    if (count($parts) > 1) {
        return strtolower(end($parts));
    }
    return '';
}

function isExtensionBlocked($filename, $blacklist) {
    $extension = getFileExtension($filename);
    return in_array($extension, $blacklist);
}

$message = "";
$success = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['attachment']) && $_FILES['attachment']['error'] === UPLOAD_ERR_OK) {
        $filename = basename($_FILES['attachment']['name']);
        $target_path = "uploads/" . $filename;
        
        // Validate using blacklist (vulnerable - incomplete blacklist)
        if (isExtensionBlocked($filename, $blocked_extensions)) {
            $message = "Error: File extension is blocked for security reasons.";
        } else {
            // Move the uploaded file
            if (move_uploaded_file($_FILES['attachment']['tmp_name'], $target_path)) {
                $message = "File uploaded successfully: " . htmlspecialchars($filename);
                $success = true;
            } else {
                $message = "Error: Failed to save file.";
            }
        }
    } else {
        $message = "Error: No file uploaded or upload error occurred.";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Result - eZ Content Manager</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>eZ Content Manager</h1>
            <p class="subtitle">Upload Result</p>
        </header>

        <main>
            <section class="result-section">
                <?php if ($success): ?>
                <div class="alert success">
                    <p><?php echo $message; ?></p>
                    <p>Your file is available at: <a href="uploads/<?php echo htmlspecialchars($filename); ?>">uploads/<?php echo htmlspecialchars($filename); ?></a></p>
                </div>
                <?php else: ?>
                <div class="alert error">
                    <p><?php echo $message; ?></p>
                </div>
                <?php endif; ?>
                
                <a href="index.php" class="btn">Back to Upload Form</a>
            </section>
        </main>

        <footer>
            <p>&copy; 2024 eZ Content Management System</p>
        </footer>
    </div>
</body>
</html>
