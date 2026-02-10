<?php
/**
 * SKU Archive Extraction Service
 * Allows extraction of TAR archives for SKU data import
 * 
 * Vulnerable to CVE-2018-1000888: Archive_Tar allows phar:// in filenames
 * The _maliciousFilename function only checks for directory traversal (../)
 * but doesn't block stream wrappers like phar://
 */

header('Content-Type: application/json');
require_once 'ReadClass.php';

$response = [
    'status' => 'failure',
    'message' => 'No archive data received.'
];

/**
 * Simulates the vulnerable _maliciousFilename function from Archive_Tar < 1.4.4
 * Only checks for directory traversal, NOT for stream wrappers like phar://
 */
function _maliciousFilename($filename) {
    // Check for directory traversal (the original vulnerable check)
    if (strpos($filename, '/../') !== false || 
        strpos($filename, '../') === 0) {
        return true; // Malicious - directory traversal
    }
    // BUG: Missing check for phar:// stream wrapper!
    // The fix adds: if (strpos($filename, 'phar://') === 0) return true;
    return false; // Allowed
}

/**
 * Parse a TAR header block (512 bytes)
 */
function parseTarHeader($block) {
    if (strlen($block) < 512) {
        return false;
    }
    
    // Check for null block (end of archive)
    if (trim($block) === '') {
        return false;
    }
    
    $header = [];
    $header['filename'] = trim(substr($block, 0, 100));
    $header['mode'] = octdec(trim(substr($block, 100, 8)));
    $header['uid'] = octdec(trim(substr($block, 108, 8)));
    $header['gid'] = octdec(trim(substr($block, 116, 8)));
    $header['size'] = octdec(trim(substr($block, 124, 12)));
    $header['mtime'] = octdec(trim(substr($block, 136, 12)));
    $header['typeflag'] = substr($block, 156, 1);
    
    // Handle UStar format for long filenames
    $prefix = trim(substr($block, 345, 155));
    if (!empty($prefix)) {
        $header['filename'] = $prefix . '/' . $header['filename'];
    }
    
    return $header;
}

/**
 * Extract TAR archive - vulnerable implementation mimicking Archive_Tar < 1.4.4
 */
function extractTar($tarData, $extractPath = '/tmp/extracted/') {
    $results = [];
    $pos = 0;
    $len = strlen($tarData);
    
    // Create extraction directory
    if (!is_dir($extractPath)) {
        mkdir($extractPath, 0755, true);
    }
    
    while ($pos < $len) {
        // Read header block (512 bytes)
        $headerBlock = substr($tarData, $pos, 512);
        $pos += 512;
        
        $header = parseTarHeader($headerBlock);
        if ($header === false) {
            break; // End of archive or invalid header
        }
        
        $filename = $header['filename'];
        $size = $header['size'];
        
        // VULNERABLE CHECK: Only checks for directory traversal, not phar://
        if (_maliciousFilename($filename)) {
            $results[] = [
                'filename' => $filename,
                'status' => 'blocked',
                'reason' => 'Malicious filename detected (directory traversal)'
            ];
            // Skip data blocks
            if ($size > 0) {
                $blocks = ceil($size / 512);
                $pos += $blocks * 512;
            }
            continue;
        }
        
        // Read file content
        $content = '';
        if ($size > 0) {
            $content = substr($tarData, $pos, $size);
            // Skip to next 512-byte boundary
            $blocks = ceil($size / 512);
            $pos += $blocks * 512;
        }
        
        // VULNERABLE OPERATION: Using filename directly in file operations
        // This triggers phar:// deserialization if filename starts with phar://
        $destPath = $filename;
        
        // If not an absolute path or stream wrapper, prepend extraction path
        if (strpos($destPath, '/') !== 0 && strpos($destPath, '://') === false) {
            $destPath = $extractPath . $destPath;
        }
        
        // The vulnerable file_exists check - triggers phar deserialization!
        if (file_exists($destPath)) {
            // File already exists - this call triggers phar deserialization
            // when destPath is like phar:///tmp/malicious.phar/anyfile
            $results[] = [
                'filename' => $filename,
                'status' => 'exists',
                'message' => 'File already exists at destination'
            ];
        } else {
            // Try to write the file (this also triggers phar deserialization)
            // For stream wrappers like phar://, the operation may fail but
            // deserialization still occurs during the file_exists or fopen call
            try {
                // This is where the vulnerability is exploited
                // file_put_contents with phar:// wrapper triggers deserialization
                $result = @file_put_contents($destPath, $content);
                if ($result !== false) {
                    $results[] = [
                        'filename' => $filename,
                        'status' => 'extracted',
                        'path' => $destPath,
                        'size' => $size
                    ];
                } else {
                    $results[] = [
                        'filename' => $filename,
                        'status' => 'failed',
                        'message' => 'Could not write file'
                    ];
                }
            } catch (Exception $e) {
                $results[] = [
                    'filename' => $filename,
                    'status' => 'error',
                    'message' => $e->getMessage()
                ];
            }
        }
    }
    
    return $results;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = isset($_POST['archive']) ? $_POST['archive'] : '';
    
    if ($data) {
        // Decode base64 encoded TAR data
        $tarData = base64_decode($data);
        
        if ($tarData === false) {
            $response['message'] = 'Invalid base64 encoding.';
        } else {
            // Start output buffering to capture any output from deserialization
            ob_start();
            
            $results = extractTar($tarData);
            
            // Capture any output (e.g., from eval in __wakeup)
            $output = ob_get_clean();
            
            $response = [
                'status' => 'success',
                'message' => 'Archive processed.',
                'results' => $results,
                'extraction_output' => $output
            ];
        }
    }
}

echo json_encode($response);
?>
