<?php
/**
 * Archive_Tar v1.4.3 - Vulnerable version
 * CVE-2018-1000888: Missing phar:// wrapper check in _maliciousFilename()
 * 
 * This simulates the vulnerable PEAR Archive_Tar library
 */

class Archive_Tar {
    private $_tarname;
    private $_temp_tarname;
    
    public function __construct($tarname) {
        $this->_tarname = $tarname;
        $this->_temp_tarname = null;
    }
    
    /**
     * Extract the archive to destination path
     */
    public function extract($dest = '') {
        if ($dest == '') {
            $dest = '/tmp/extracted/';
        }
        
        if (!file_exists($this->_tarname)) {
            return ['error' => 'Archive file not found'];
        }
        
        // Read TAR file
        $handle = fopen($this->_tarname, 'rb');
        if (!$handle) {
            return ['error' => 'Failed to open archive'];
        }
        
        $extracted = [];
        
        while (!feof($handle)) {
            // Read 512-byte header block
            $header = fread($handle, 512);
            if (strlen($header) < 512) break;
            
            // Parse header
            $parsed = $this->_parseHeader($header);
            if (!$parsed || $parsed['filename'] === '') break;
            
            // Check for malicious filename (VULNERABLE - missing phar:// check)
            if ($this->_maliciousFilename($parsed['filename'])) {
                continue; // Skip malicious files
            }
            
            // Calculate padding
            $size = $parsed['size'];
            $blocks = ceil($size / 512);
            
            // Read file content
            $content = '';
            for ($i = 0; $i < $blocks; $i++) {
                $content .= fread($handle, 512);
            }
            $content = substr($content, 0, $size);
            
            // Process the file - THIS IS WHERE THE VULNERABILITY TRIGGERS
            // If filename starts with a stream wrapper like phar://, use it directly
            // This is the CVE-2018-1000888 vulnerability - phar:// paths aren't blocked
            $filename = $parsed['filename'];
            
            // Determine target path - if it's an absolute path or wrapper, use directly
            if (strpos($filename, '://') !== false || $filename[0] === '/') {
                $targetPath = $filename;
            } else {
                $targetPath = rtrim($dest, '/') . '/' . $filename;
            }
            
            // The vulnerability: file operations on phar:// paths trigger deserialization
            // file_exists() will trigger phar metadata unserialization
            if (file_exists($targetPath)) {
                // File exists - for phar://, this triggers deserialization!
                $extracted[] = ['file' => $filename, 'status' => 'exists', 'path' => $targetPath];
            } else {
                // Try to create parent directory and write file
                $dir = dirname($targetPath);
                if (!is_dir($dir) && strpos($targetPath, '://') === false) {
                    @mkdir($dir, 0755, true);
                }
                
                // file_put_contents on phar:// also triggers deserialization
                if (@file_put_contents($targetPath, $content) !== false) {
                    $extracted[] = ['file' => $filename, 'status' => 'extracted', 'path' => $targetPath];
                } else {
                    $extracted[] = ['file' => $filename, 'status' => 'processed', 'path' => $targetPath];
                }
            }
        }
        
        fclose($handle);
        return ['success' => true, 'files' => $extracted];
    }
    
    /**
     * VULNERABLE: This check is incomplete - missing phar:// wrapper check
     * Fixed in Archive_Tar 1.4.4
     */
    private function _maliciousFilename($filename) {
        // Check for directory traversal
        if (strpos($filename, '/../') !== false) {
            return true;
        }
        if (strpos($filename, '../') === 0) {
            return true;
        }
        // MISSING: Check for phar:// prefix (CVE-2018-1000888)
        // The fix would be: if (strpos($filename, 'phar://') === 0) return true;
        return false;
    }
    
    /**
     * Parse TAR header
     */
    private function _parseHeader($header) {
        // Check if header is empty (all nulls)
        if (trim($header, "\0") === '') {
            return null;
        }
        
        $parsed = [];
        
        // Extract filename (bytes 0-99)
        $parsed['filename'] = trim(substr($header, 0, 100), "\0");
        
        // Extract size (bytes 124-135, octal)
        $size_str = trim(substr($header, 124, 12), "\0 ");
        $parsed['size'] = octdec($size_str);
        
        // Extract file type (byte 156)
        $parsed['type'] = substr($header, 156, 1);
        
        return $parsed;
    }
    
    public function __destruct() {
        // Cleanup temp file if exists
        if ($this->_temp_tarname && file_exists($this->_temp_tarname)) {
            @unlink($this->_temp_tarname);
        }
    }
}
?>
