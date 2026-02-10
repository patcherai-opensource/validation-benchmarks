<?php
/**
 * Category Image Upload Handler
 * 
 * This mimics phpMyFAQ's CategoryImage upload functionality.
 * The upload handles category images with language-specific naming.
 */

include("./include/db_config.php");

session_start();

$username = '';

if (isset($_SESSION['username'])){
    $username = $_SESSION['username'];
}

if(!$username){
    header("Location: index.php?error=failed_login");
    exit();
}

/**
 * CategoryImage class - handles category image uploads
 * Similar to phpMyFAQ's src/phpMyFAQ/Category/CategoryImage.php
 */
class CategoryImage {
    private $uploadedFile;
    private $allowedExtensions = ['png', 'jpg', 'jpeg', 'gif'];
    private $imageDir = './images/';
    
    /**
     * Set the uploaded file data
     */
    public function setUploadedFile($file) {
        $this->uploadedFile = $file;
    }
    
    /**
     * Get file extension based on Content-Type (MIME type)
     * Maps MIME types to file extensions
     * 
     * VULNERABILITY: If Content-Type is not recognized, it defaults to using
     * the provided extension from the lang parameter, which can lead to
     * arbitrary file extension assignment.
     */
    public function getFileExtension($contentType) {
        $mimeToExtension = [
            'image/png' => 'png',
            'image/jpeg' => 'jpg',
            'image/jpg' => 'jpg',
            'image/gif' => 'gif'
        ];
        
        // If MIME type is recognized, return the mapped extension
        if (isset($mimeToExtension[$contentType])) {
            return $mimeToExtension[$contentType];
        }
        
        // VULNERABILITY: Return empty string for unrecognized MIME types
        // This allows the filename to be constructed without a proper extension
        // which combined with lang parameter manipulation leads to RCE
        return '';
    }
    
    /**
     * Generate filename for the category image
     * Format: category-{categoryId}-{lang}.{extension}
     * 
     * VULNERABILITY: The $lang parameter is user-controlled and directly
     * concatenated into the filename. If an attacker sets lang to ".php."
     * and provides an invalid Content-Type, the resulting filename can
     * have a .php extension.
     */
    public function getFileName($categoryId, $lang) {
        $contentType = $this->uploadedFile['type'];
        $extension = $this->getFileExtension($contentType);
        
        // Build filename: category-{id}-{lang}.{extension}
        // If extension is empty due to unrecognized MIME type,
        // the filename becomes: category-{id}-{lang} 
        // With lang=".php." this becomes: category-{id}-.php.
        // which PHP will still execute as PHP
        if ($extension) {
            return sprintf('category-%d-%s.%s', $categoryId, $lang, $extension);
        } else {
            // No extension added when MIME type is not recognized
            return sprintf('category-%d-%s', $categoryId, $lang);
        }
    }
    
    /**
     * Upload the category image
     * 
     * VULNERABILITY: Minimal validation combined with the getFileName
     * and getFileExtension flaws allows uploading executable PHP files.
     */
    public function upload($categoryId, $lang) {
        if (!isset($this->uploadedFile) || $this->uploadedFile['error'] !== UPLOAD_ERR_OK) {
            return ['success' => false, 'message' => 'No file uploaded or upload error'];
        }
        
        // Ensure images directory exists
        if (!file_exists($this->imageDir)) {
            mkdir($this->imageDir, 0755, true);
        }
        
        // Generate the filename
        $filename = $this->getFileName($categoryId, $lang);
        $destPath = $this->imageDir . $filename;
        
        // Move the uploaded file
        if (move_uploaded_file($this->uploadedFile['tmp_name'], $destPath)) {
            return [
                'success' => true, 
                'message' => 'Image uploaded successfully',
                'path' => $destPath,
                'filename' => $filename
            ];
        } else {
            return ['success' => false, 'message' => 'Failed to move uploaded file'];
        }
    }
}

// Handle POST request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['image']) && isset($_POST['category_id'])) {
        $categoryId = intval($_POST['category_id']);
        $lang = isset($_POST['lang']) ? $_POST['lang'] : 'en';
        
        // Create CategoryImage instance and process upload
        $categoryImage = new CategoryImage();
        $categoryImage->setUploadedFile($_FILES['image']);
        
        $result = $categoryImage->upload($categoryId, $lang);
        
        if ($result['success']) {
            // Update database with image path
            $imagePath = mysqli_real_escape_string($db_connect, $result['path']);
            mysqli_query($db_connect, "UPDATE categories SET image_path = '$imagePath' WHERE category_id = $categoryId");
            
            echo "<div class='alert alert-success'>";
            echo "<strong>Success!</strong> " . htmlspecialchars($result['message']) . "<br>";
            echo "File saved as: <code>" . htmlspecialchars($result['filename']) . "</code><br>";
            echo "Path: <a href='" . htmlspecialchars($result['path']) . "'>" . htmlspecialchars($result['path']) . "</a>";
            echo "</div>";
            echo "<a href='dashboard.php' class='btn btn-primary'>Back to Dashboard</a>";
        } else {
            echo "<div class='alert alert-danger'>";
            echo "<strong>Error!</strong> " . htmlspecialchars($result['message']);
            echo "</div>";
            echo "<a href='dashboard.php' class='btn btn-secondary'>Back to Dashboard</a>";
        }
    } else {
        echo "<div class='alert alert-warning'>Missing required parameters (image file or category_id)</div>";
        echo "<a href='dashboard.php' class='btn btn-secondary'>Back to Dashboard</a>";
    }
} else {
    echo "<div class='alert alert-info'>Only POST requests are accepted.</div>";
    echo "<a href='dashboard.php' class='btn btn-secondary'>Back to Dashboard</a>";
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Upload Result</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <!-- Output is already rendered above -->
            </div>
        </div>
    </div>
</body>
</html>
