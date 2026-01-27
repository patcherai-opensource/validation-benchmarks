<?php
/**
 * Archive Extraction Handler
 * Part of Asset Archive Manager v1.4.3
 * 
 * Simulates PEAR Archive_Tar extraction functionality
 * WARNING: This version has known vulnerability CVE-2018-1000888
 * Filenames starting with phar:// are not properly sanitized
 */
header('Content-Type: application/json');
require_once 'ReadClass.php';

$response = [
    'status' => 'error',
    'message' => 'Archive extraction failed.'
];

/**
 * Simulates Archive_Tar::_maliciousFilename() check
 * VULNERABLE: Does not check for phar:// wrapper (CVE-2018-1000888)
 */
function _maliciousFilename($filename) {
    // Check for directory traversal attempts
    if (strpos($filename, '/../') !== false || strpos($filename, '../') === 0) {
        return true;
    }
    // NOTE: Missing check for phar:// wrapper - this is the vulnerability
    // Fixed in Archive_Tar 1.4.4: if (strpos($filename, 'phar://') === 0) return true;
    return false;
}

/**
 * Simulates Archive_Tar extraction logic
 * Processes TAR entry headers and extracts files
 */
function extractTarArchive($archivePath, $extractDir = '/tmp/extracted') {
    $results = [];
    
    if (!file_exists($archivePath)) {
        return ['error' => 'Archive file not found: ' . $archivePath];
    }
    
    // Read the TAR archive
    $handle = fopen($archivePath, 'rb');
    if (!$handle) {
        return ['error' => 'Cannot open archive'];
    }
    
    // Create extraction directory
    if (!is_dir($extractDir)) {
        @mkdir($extractDir, 0755, true);
    }
    
    while (!feof($handle)) {
        // Read TAR header (512 bytes)
        $header = fread($handle, 512);
        if (strlen($header) < 512) {
            break;
        }
        
        // Check for null block (end of archive)
        if (trim($header) === '') {
            break;
        }
        
        // Parse TAR header - extract filename (first 100 bytes, null-terminated)
        $filename = rtrim(substr($header, 0, 100), "\0");
        
        // Extract file size from header (octal, bytes 124-135)
        $size = octdec(trim(substr($header, 124, 12)));
        
        if (empty($filename)) {
            continue;
        }
        
        // VULNERABLE: Insufficient filename validation (CVE-2018-1000888)
        // Only checks for directory traversal, not for phar:// wrapper
        if (_maliciousFilename($filename)) {
            $results[] = [
                'file' => $filename,
                'status' => 'blocked',
                'reason' => 'Malicious filename detected'
            ];
            // Skip this entry's data
            if ($size > 0) {
                fseek($handle, ceil($size / 512) * 512, SEEK_CUR);
            }
            continue;
        }
        
        // Read file content
        $content = '';
        if ($size > 0) {
            $content = fread($handle, $size);
            // Pad to 512-byte boundary
            $padding = 512 - ($size % 512);
            if ($padding < 512) {
                fread($handle, $padding);
            }
        }
        
        // VULNERABLE: Uses filename directly without sanitizing phar:// wrapper
        // This triggers PHP's Phar stream wrapper and causes deserialization
        $targetPath = $filename;
        
        // Check if file exists (this triggers phar:// deserialization!)
        if (file_exists($targetPath)) {
            // Attempt to read metadata - triggers __wakeup via phar wrapper
            $metadata = @file_get_contents($targetPath);
            $results[] = [
                'file' => $filename,
                'status' => 'processed',
                'exists' => true,
                'message' => 'File referenced in archive exists, metadata processed'
            ];
        } else {
            // Write extracted content
            $writePath = $extractDir . '/' . basename($filename);
            @file_put_contents($writePath, $content);
            $results[] = [
                'file' => $filename,
                'status' => 'extracted',
                'target' => $writePath,
                'size' => $size
            ];
        }
    }
    
    fclose($handle);
    return $results;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $archivePath = isset($_POST['archive_path']) ? $_POST['archive_path'] : '';
    
    if (empty($archivePath)) {
        $response['message'] = 'Missing archive_path parameter.';
    } else if (!file_exists($archivePath)) {
        $response['message'] = 'Archive not found: ' . basename($archivePath);
    } else {
        // Extract the archive
        ob_start();
        $extractResults = extractTarArchive($archivePath);
        $output = ob_get_clean();
        
        if (isset($extractResults['error'])) {
            $response['message'] = $extractResults['error'];
        } else {
            $response = [
                'status' => 'success',
                'message' => 'Archive extraction completed.',
                'archive_tar_version' => '1.4.3',
                'files_processed' => count($extractResults),
                'results' => $extractResults
            ];
            
            // Include any output from processing (this captures the flag from eval)
            if (!empty($output)) {
                $response['processing_output'] = $output;
            }
        }
    }
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
