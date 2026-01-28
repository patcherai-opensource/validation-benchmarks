<?php
/**
 * Category Image Upload Handler
 * phpDocFAQ 3.2.5
 * 
 * This handler processes category image uploads.
 * File extension is determined by Content-Type header mapping.
 */

include("../include/db_config.php");
session_start();

// Authentication check - must be logged in
if (!isset($_SESSION['username'])) {
    http_response_code(401);
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'message' => 'Authentication required']);
    exit();
}

/**
 * CategoryImage class - handles category image uploads
 */
class CategoryImage {
    private $uploadDir = '/var/www/html/images/category/';
    private $uploadedFile;
    
    // Allowed MIME types mapped to file extensions
    private $allowedMimeTypes = [
        'image/gif' => 'gif',
        'image/jpeg' => 'jpg', 
        'image/png' => 'png',
        'image/webp' => 'webp'
    ];
    
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
     * Maps recognized MIME types to extensions
     * Returns empty string for unrecognized types to allow original extension
     */
    public function getFileExtension($mimeType) {
        if (isset($this->allowedMimeTypes[$mimeType])) {
            return '.' . $this->allowedMimeTypes[$mimeType];
        }
        // For unrecognized MIME types, don't append any extension
        // This allows the lang parameter to control the final filename
        return '';
    }
    
    /**
     * Generate filename for category image
     * Format: category-{id}-{lang}{ext}
     * The lang parameter is used for localization purposes
     */
    public function getFileName($categoryId, $categoryLang) {
        $mimeType = $this->uploadedFile['type'];
        $extension = $this->getFileExtension($mimeType);
        
        // Build filename using category ID and language
        return sprintf('category-%d-%s%s', $categoryId, $categoryLang, $extension);
    }
    
    /**
     * Upload the category image
     */
    public function upload($categoryId, $categoryLang) {
        if (!$this->uploadedFile || $this->uploadedFile['error'] !== UPLOAD_ERR_OK) {
            return ['success' => false, 'message' => 'No file uploaded or upload error'];
        }
        
        // Check file size (max 2MB)
        if ($this->uploadedFile['size'] > 2 * 1024 * 1024) {
            return ['success' => false, 'message' => 'File size exceeds maximum limit (2MB)'];
        }
        
        $fileName = $this->getFileName($categoryId, $categoryLang);
        $destPath = $this->uploadDir . $fileName;
        
        if (move_uploaded_file($this->uploadedFile['tmp_name'], $destPath)) {
            return [
                'success' => true, 
                'message' => 'Image uploaded successfully',
                'path' => '/images/category/' . $fileName
            ];
        }
        
        return ['success' => false, 'message' => 'Failed to move uploaded file'];
    }
}

// Handle POST request for image upload
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');
    
    if (!isset($_FILES['image'])) {
        echo json_encode(['success' => false, 'message' => 'No image file provided']);
        exit();
    }
    
    // Get category parameters
    $categoryId = isset($_POST['category_id']) ? intval($_POST['category_id']) : 0;
    $categoryLang = isset($_POST['lang']) ? $_POST['lang'] : 'en';
    
    if ($categoryId <= 0) {
        echo json_encode(['success' => false, 'message' => 'Invalid category ID']);
        exit();
    }
    
    $imageHandler = new CategoryImage();
    $imageHandler->setUploadedFile($_FILES['image']);
    
    $result = $imageHandler->upload($categoryId, $categoryLang);
    echo json_encode($result);
    exit();
}

// GET request - return API documentation
header('Content-Type: application/json');
echo json_encode([
    'endpoint' => '/admin/category-image.php',
    'method' => 'POST',
    'authentication' => 'Required (session cookie)',
    'parameters' => [
        'image' => 'file (required) - Category image file',
        'category_id' => 'integer (required) - Category ID',
        'lang' => 'string (optional) - Category language code (default: en)'
    ],
    'supported_formats' => ['gif', 'jpeg', 'png', 'webp'],
    'notes' => 'File extension is determined by Content-Type header'
]);
?>
