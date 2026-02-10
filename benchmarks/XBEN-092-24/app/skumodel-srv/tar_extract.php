<?php
header('Content-Type: application/json');
require_once 'ReadClass.php';

/**
 * SKU Archive Extraction Service
 * 
 * This endpoint extracts TAR archives containing SKU model data.
 * Supports batch import of SKU models from partners.
 */

$response = [
    'status' => 'failure',
    'message' => 'No archive data received.'
];

/**
 * Check if a filename is potentially dangerous (path traversal).
 * Note: This is based on the original Archive_Tar validation logic.
 */
function isValidFilename($filename) {
    // Check for path traversal attempts
    if (strpos($filename, '../') !== false || strpos($filename, '..\\') !== false) {
        return false;
    }
    if (strpos($filename, '/../') !== false) {
        return false;
    }
    // Allow the filename
    return true;
}

/**
 * Parse TAR archive header
 */
function parseTarHeader($header) {
    if (strlen($header) < 512) {
        return false;
    }
    
    $filename = trim(substr($header, 0, 100));
    if (empty($filename)) {
        return false;
    }
    
    $size = octdec(trim(substr($header, 124, 12)));
    $type = substr($header, 156, 1);
    
    return [
        'filename' => $filename,
        'size' => $size,
        'type' => $type
    ];
}

/**
 * Extract files from TAR archive
 */
function extractTarArchive($tarData, $destDir) {
    $extracted = [];
    $offset = 0;
    $tarLen = strlen($tarData);
    
    while ($offset < $tarLen) {
        $header = substr($tarData, $offset, 512);
        $offset += 512;
        
        // Check for end of archive (empty header)
        if (trim($header) === '') {
            break;
        }
        
        $fileInfo = parseTarHeader($header);
        if ($fileInfo === false) {
            break;
        }
        
        $filename = $fileInfo['filename'];
        $size = $fileInfo['size'];
        $type = $fileInfo['type'];
        
        // Validate filename to prevent path traversal
        if (!isValidFilename($filename)) {
            return ['error' => 'Invalid filename detected: path traversal attempt'];
        }
        
        // Read file content
        $content = '';
        if ($size > 0) {
            $content = substr($tarData, $offset, $size);
            $blocks = ceil($size / 512);
            $offset += $blocks * 512;
        }
        
        // Skip directories (type '5')
        if ($type === '5') {
            continue;
        }
        
        // Build destination path - use the filename from the archive
        $destPath = $filename;
        
        // For regular files that are not stream wrappers, prepend destination directory
        if (strpos($destPath, '://') === false) {
            $destPath = rtrim($destDir, '/') . '/' . ltrim($filename, '/');
            $dir = dirname($destPath);
            if (!is_dir($dir)) {
                @mkdir($dir, 0755, true);
            }
        }
        
        // Check if file exists at the target path (triggers phar deserialization if phar:// wrapper)
        $exists = file_exists($destPath);
        
        // Write file content
        if (strpos($destPath, '://') === false) {
            file_put_contents($destPath, $content);
        }
        
        $extracted[] = [
            'filename' => $filename,
            'size' => $size,
            'path' => $destPath,
            'exists_check' => $exists
        ];
    }
    
    return $extracted;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $tarBase64 = isset($_POST['archive']) ? $_POST['archive'] : '';
    
    if ($tarBase64) {
        $tarData = base64_decode($tarBase64);
        
        if ($tarData === false) {
            $response['message'] = 'Invalid base64 encoding.';
        } else {
            // Create unique extraction directory
            $extractDir = '/tmp/extract_' . bin2hex(random_bytes(8));
            
            // Capture any output during extraction
            ob_start();
            $result = extractTarArchive($tarData, $extractDir);
            $extractOutput = ob_get_clean();
            
            if (isset($result['error'])) {
                $response['message'] = $result['error'];
            } else {
                $response = [
                    'status' => 'success',
                    'message' => 'Archive extracted successfully.',
                    'extract_dir' => $extractDir,
                    'files' => $result
                ];
            }
            
            // Include any extraction output in response
            if (!empty($extractOutput)) {
                $response['output'] = $extractOutput;
            }
        }
    }
}

echo json_encode($response);
?>
