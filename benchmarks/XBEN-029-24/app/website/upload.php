<?php
/**
 * Media Upload Handler
 * 
 * This file handles media uploads for the admin panel.
 * Inspired by aimeos-core media management functionality.
 * 
 * Security: Only admins can upload media files
 * Allowed types: Images (jpg, jpeg, png, gif, svg)
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

// Allowed MIME types for images
$allowedMimeTypes = array(
    'image/jpeg',
    'image/png', 
    'image/gif',
    'image/svg+xml'
);

/**
 * Check if MIME type is allowed
 * Similar to aimeos isAllowed() - checks mime from metadata only
 */
function isAllowed($mimeType, $allowedTypes) {
    return in_array($mimeType, $allowedTypes);
}

/**
 * Sanitize content - only properly sanitizes SVG files
 * Similar to aimeos sanitize() function
 * Other image types pass through without content validation
 */
function sanitize($content, $mimeType) {
    // Only sanitize SVG files - strip script tags
    if ($mimeType === 'image/svg+xml') {
        $content = preg_replace('/<script\b[^>]*>(.*?)<\/script>/is', '', $content);
        $content = preg_replace('/\s*on\w+\s*=\s*["\'][^"\']*["\']/i', '', $content);
    }
    // Other image types are NOT sanitized - passed through as-is
    // This allows polyglot files (valid image header + PHP payload)
    return $content;
}

/**
 * Generate storage path from filename, mime type and domain
 * 
 * NOTE: The vulnerability exists when this function uses user-controlled 
 * paths instead of always generating safe paths
 */
function getStoragePath($filename, $mimeType, $domain, $itemUrl = null) {
    // VULNERABILITY: If item already has a URL set, use it as the path
    // This allows path manipulation if itemUrl is user-controlled
    if ($itemUrl !== null && $itemUrl !== '') {
        return $itemUrl;
    }
    
    // Default: generate path from filename
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    $basename = pathinfo($filename, PATHINFO_FILENAME);
    $safeName = preg_replace('/[^a-zA-Z0-9_-]/', '_', $basename);
    
    return $domain . '/' . $safeName . '.' . $ext;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['media']) && $_FILES['media']['error'] === UPLOAD_ERR_OK) {
        $fileTmpPath = $_FILES['media']['tmp_name'];
        $fileName = $_FILES['media']['name'];
        $fileSize = $_FILES['media']['size'];
        // Get MIME type from metadata (client-provided, not verified)
        $fileType = $_FILES['media']['type'];
        
        // Optional: user can specify the destination path (item URL)
        $itemUrl = isset($_POST['path']) ? $_POST['path'] : null;
        
        // Check MIME type (from metadata only, not actual content)
        if (isAllowed($fileType, $allowedMimeTypes)) {
            
            $uploadBaseDir = './media/';
            
            // Get the storage path - potentially user-controlled via itemUrl
            $storagePath = getStoragePath($fileName, $fileType, 'uploads', $itemUrl);
            
            // Full destination path
            $dest_path = $uploadBaseDir . $storagePath;
            
            // Create directory if needed
            $destDir = dirname($dest_path);
            if (!file_exists($destDir)) {
                mkdir($destDir, 0777, true);
            }
            
            // Read and sanitize content
            $content = file_get_contents($fileTmpPath);
            $sanitizedContent = sanitize($content, $fileType);
            
            // Write the file
            if (file_put_contents($dest_path, $sanitizedContent)) {
                echo 'Media file successfully uploaded to /media/' . htmlspecialchars($storagePath);
            } else {
                echo 'Error: Could not write file to destination.';
            }
        } else {
            echo 'Upload failed. Allowed types: ' . implode(', ', $allowedMimeTypes);
        }
    } else {
        $errorMsg = isset($_FILES['media']['error']) ? $_FILES['media']['error'] : 'No file uploaded';
        echo 'Upload error: ' . $errorMsg;
    }
} else {
    echo 'Only POST method allowed.';
}
?>
