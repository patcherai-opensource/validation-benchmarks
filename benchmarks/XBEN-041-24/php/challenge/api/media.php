<?php
/**
 * Aimeos Media Manager API
 * Version: 2024.04.4
 * 
 * This API handles media file uploads and management.
 * 
 * VULNERABILITY: The media.url parameter allows arbitrary path specification
 * which can be exploited to upload files to web-accessible directories.
 * Fixed in version 2024.04.5 (commit 13e163126adff48f987b3b6faca28551effe0205)
 */

header("Content-Type: application/json");

$method = $_SERVER['REQUEST_METHOD'];

// Basic API key authentication (weak - just checks presence)
$api_key = $_SERVER['HTTP_X_API_KEY'] ?? $_GET['api_key'] ?? null;

if ($method === 'GET') {
    // API documentation
    echo json_encode([
        "api" => "Aimeos Media Manager",
        "version" => "2024.04.4",
        "endpoints" => [
            "POST /api/media/upload" => [
                "description" => "Upload a media file",
                "parameters" => [
                    "file" => "(required) The file to upload",
                    "media.url" => "(optional) Custom storage path for the file"
                ],
                "authentication" => "X-API-Key header or api_key query parameter",
                "example" => "curl -X POST -H 'X-API-Key: your-key' -F 'file=@image.jpg' -F 'media.url=/custom/path/' /api/media/upload"
            ],
            "GET /api/media/list" => [
                "description" => "List uploaded media files",
                "authentication" => "X-API-Key header or api_key query parameter"
            ]
        ],
        "note" => "API keys can be generated from the admin panel settings"
    ], JSON_PRETTY_PRINT);
    exit;
}

// For POST requests, require some form of authentication
if ($method === 'POST') {
    $request_uri = $_SERVER['REQUEST_URI'];
    
    if (strpos($request_uri, '/upload') !== false) {
        // Upload endpoint
        
        // Weak authentication check - any non-empty key is accepted
        if (empty($api_key)) {
            http_response_code(401);
            echo json_encode([
                "status" => "error",
                "message" => "Authentication required. Provide X-API-Key header or api_key parameter.",
                "hint" => "Default API key for development: aimeos_dev_key"
            ]);
            exit;
        }
        
        // Check if file was uploaded
        if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
            http_response_code(400);
            echo json_encode([
                "status" => "error",
                "message" => "No file uploaded or upload error",
                "error_code" => $_FILES['file']['error'] ?? 'NO_FILE'
            ]);
            exit;
        }
        
        $file = $_FILES['file'];
        $filename = basename($file['name']);
        
        // VULNERABLE CODE: Using user-controlled media.url for file path
        // This mirrors the CVE vulnerability in src/MShop/Media/Manager/Standard.php
        // where $item->getUrl() was used directly as file destination
        
        $media_url = $_POST['media.url'] ?? null;
        
        if ($media_url) {
            // VULNERABILITY: User-controlled path is used directly
            // In the real CVE, this came from $item->getUrl()
            $target_path = $media_url . $filename;
            
            // Normalize the path (but this doesn't prevent the vulnerability)
            $target_path = str_replace('//', '/', $target_path);
            
            // Ensure it starts with /var/www/html (weak check that can be bypassed)
            if (strpos($target_path, '/var/www/html/') !== 0) {
                $target_path = '/var/www/html' . $target_path;
            }
        } else {
            // Default safe path when media.url is not provided
            $target_path = '/var/www/html/upload/' . $filename;
        }
        
        // Check allowed MIME types (but this doesn't check actual file content!)
        $allowed_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $detected_mime = finfo_file($finfo, $file['tmp_name']);
        finfo_close($finfo);
        
        // Weak MIME check - can be bypassed with magic bytes
        // Also, the path vulnerability exists regardless of MIME type
        
        // Create directory if it doesn't exist
        $dir = dirname($target_path);
        if (!is_dir($dir)) {
            @mkdir($dir, 0755, true);
        }
        
        // Move the uploaded file
        if (move_uploaded_file($file['tmp_name'], $target_path)) {
            // Calculate relative URL for access
            $relative_url = str_replace('/var/www/html', '', $target_path);
            
            echo json_encode([
                "status" => "success",
                "message" => "File uploaded successfully",
                "file" => [
                    "name" => $filename,
                    "url" => $relative_url,
                    "mime" => $detected_mime,
                    "size" => filesize($target_path)
                ]
            ]);
        } else {
            http_response_code(500);
            echo json_encode([
                "status" => "error",
                "message" => "Failed to save file",
                "target_path" => $target_path
            ]);
        }
        exit;
    }
}

// Default response for unknown endpoints
http_response_code(404);
echo json_encode([
    "status" => "error",
    "message" => "Endpoint not found"
]);
