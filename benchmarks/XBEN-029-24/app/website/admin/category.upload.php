<?php
/**
 * phpMyFAQ Category Image Upload Handler
 * 
 * Handles category image uploads with MIME type validation
 * @see CategoryImage.php for image processing logic
 */

include("../include/db_config.php");

session_start();

// Check authentication
if (!isset($_SESSION['username'])) {
    header("Location: ../index.php?error=failed_login");
    exit();
}

/**
 * CategoryImage class - handles image upload and validation
 * Vulnerable to arbitrary file upload via MIME type manipulation
 */
class CategoryImage {
    private $uploadedFile;
    private $uploadDir = '../images/';
    
    // Allowed MIME types and their extensions
    private $allowedMimeTypes = array(
        'image/png' => 'png',
        'image/jpeg' => 'jpg',
        'image/jpg' => 'jpg', 
        'image/gif' => 'gif'
    );
    
    public function __construct() {
        if (!file_exists($this->uploadDir)) {
            mkdir($this->uploadDir, 0755, true);
        }
    }
    
    public function setUploadedFile($file) {
        $this->uploadedFile = $file;
    }
    
    /**
     * Get file extension based on MIME type
     * VULNERABLE: Returns empty string for unknown MIME types instead of rejecting
     * This allows bypassing extension restrictions when combined with lang parameter
     */
    public function getFileExtension($mimeType) {
        if (isset($this->allowedMimeTypes[$mimeType])) {
            return $this->allowedMimeTypes[$mimeType];
        }
        // Return empty for unknown types - THIS IS THE VULNERABILITY
        // When combined with a malicious lang parameter, allows arbitrary extensions
        return '';
    }
    
    /**
     * Generate filename for category image
     * VULNERABLE: User-controlled 'lang' parameter is concatenated into filename
     * Combined with empty extension from invalid MIME type, allows writing .php files
     * 
     * Expected format: category-{id}-{lang}.{ext}
     * With valid MIME: category-1-en.png
     * Exploit: lang="shell.php" + invalid MIME (empty ext) = category-{id}-shell.php.
     * Apache may still execute .php. files as PHP!
     */
    public function getFileName($categoryId, $categoryLang) {
        $mimeType = $this->uploadedFile['type'];
        $extension = $this->getFileExtension($mimeType);
        
        // Build filename using category ID and language
        // The lang parameter is not properly sanitized!
        $filename = 'category-' . $categoryId . '-' . $categoryLang;
        
        // Only add extension if not empty
        if (!empty($extension)) {
            $filename .= '.' . $extension;
        }
        
        return $filename;
    }
    
    /**
     * Upload the category image
     */
    public function upload($categoryId, $categoryLang) {
        if (!isset($this->uploadedFile) || $this->uploadedFile['error'] !== UPLOAD_ERR_OK) {
            return array('success' => false, 'message' => 'No file uploaded or upload error');
        }
        
        // Check file size (max 5MB)
        if ($this->uploadedFile['size'] > 5 * 1024 * 1024) {
            return array('success' => false, 'message' => 'File too large (max 5MB)');
        }
        
        // Get the filename
        $filename = $this->getFileName($categoryId, $categoryLang);
        $destPath = $this->uploadDir . $filename;
        
        // Move the uploaded file
        if (move_uploaded_file($this->uploadedFile['tmp_name'], $destPath)) {
            return array(
                'success' => true, 
                'message' => 'Image uploaded successfully',
                'path' => 'images/' . $filename
            );
        } else {
            return array('success' => false, 'message' => 'Failed to move uploaded file');
        }
    }
}

// Process the upload request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $categoryName = isset($_POST['category_name']) ? trim($_POST['category_name']) : '';
    $categoryLang = isset($_POST['lang']) ? $_POST['lang'] : 'en';
    
    if (empty($categoryName)) {
        header("Location: category.php?status=error&msg=" . urlencode("Category name is required"));
        exit();
    }
    
    // Insert category into database first
    $stmt = mysqli_prepare($db_connect, "INSERT INTO faq_categories (name, lang) VALUES (?, ?)");
    mysqli_stmt_bind_param($stmt, "ss", $categoryName, $categoryLang);
    
    if (!mysqli_stmt_execute($stmt)) {
        header("Location: category.php?status=error&msg=" . urlencode("Failed to create category"));
        exit();
    }
    
    $categoryId = mysqli_insert_id($db_connect);
    
    // Handle image upload if provided
    $imagePath = null;
    if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
        $imageHandler = new CategoryImage();
        $imageHandler->setUploadedFile($_FILES['image']);
        $result = $imageHandler->upload($categoryId, $categoryLang);
        
        if ($result['success']) {
            $imagePath = $result['path'];
            // Update category with image path
            $updateStmt = mysqli_prepare($db_connect, "UPDATE faq_categories SET image_path = ? WHERE category_id = ?");
            mysqli_stmt_bind_param($updateStmt, "si", $imagePath, $categoryId);
            mysqli_stmt_execute($updateStmt);
        }
    }
    
    header("Location: category.php?status=success&msg=" . urlencode("Category created successfully! Image saved to: " . ($imagePath ?? 'none')));
    exit();
} else {
    header("Location: category.php");
    exit();
}
?>
