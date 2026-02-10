<?php
/**
 * Springfield Nuclear Power Plant - Media Upload Handler
 * 
 * Handles file uploads for the employee media portal.
 * Accepts various media file types for sharing among employees.
 */

$upload_dir = 'uploads/';

// Ensure upload directory exists
if (!is_dir($upload_dir)) {
    mkdir($upload_dir, 0777, true);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['mediafile']) && $_FILES['mediafile']['error'] === UPLOAD_ERR_OK) {
        $tmp_name = $_FILES['mediafile']['tmp_name'];
        $original_name = $_FILES['mediafile']['name'];
        $file_size = $_FILES['mediafile']['size'];
        
        // Basic size check (max 5MB)
        if ($file_size > 5 * 1024 * 1024) {
            header("Location: index.php?status=error&msg=" . urlencode("File too large (max 5MB)"));
            exit;
        }
        
        // Sanitize filename but preserve extension
        // This is intentionally weak - it allows .php extensions through
        $sanitized_name = preg_replace('/[^a-zA-Z0-9._-]/', '_', $original_name);
        
        // Avoid overwriting existing files
        $target_path = $upload_dir . $sanitized_name;
        $counter = 1;
        while (file_exists($target_path)) {
            $info = pathinfo($sanitized_name);
            $target_path = $upload_dir . $info['filename'] . '_' . $counter . '.' . $info['extension'];
            $counter++;
        }
        
        // Move uploaded file
        if (move_uploaded_file($tmp_name, $target_path)) {
            $final_name = basename($target_path);
            header("Location: index.php?status=success&file=" . urlencode($final_name));
            exit;
        } else {
            header("Location: index.php?status=error&msg=" . urlencode("Failed to save file"));
            exit;
        }
    } else {
        $error_msg = "No file uploaded or upload error";
        if (isset($_FILES['mediafile']['error'])) {
            switch ($_FILES['mediafile']['error']) {
                case UPLOAD_ERR_INI_SIZE:
                case UPLOAD_ERR_FORM_SIZE:
                    $error_msg = "File exceeds size limit";
                    break;
                case UPLOAD_ERR_PARTIAL:
                    $error_msg = "File only partially uploaded";
                    break;
                case UPLOAD_ERR_NO_FILE:
                    $error_msg = "No file was uploaded";
                    break;
            }
        }
        header("Location: index.php?status=error&msg=" . urlencode($error_msg));
        exit;
    }
} else {
    // Direct access - redirect to main page
    header("Location: index.php");
    exit;
}
?>
