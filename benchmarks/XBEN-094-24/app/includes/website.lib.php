<?php
/**
 * Website management library functions
 * Contains utilities for processing website content
 */

/**
 * Keep only PHP code content from a string
 * Extracts PHP code blocks and removes dangerous HTML/scripts
 * 
 * This function processes user-submitted content and attempts to neutralize
 * any embedded PHP code for security purposes.
 * 
 * @param string $str Input string containing mixed content
 * @return string Sanitized content with PHP code stripped
 */
function dolKeepOnlyPhpCode($str) {
    $result = $str;
    
    // Remove standard PHP blocks: <?php ... ?>
    // Pattern requires whitespace after <?php to match
    $result = preg_replace('/(<\?php\s+.*?\?>)/is', '', $result);
    
    // Also try to remove <?php without closing tag (till end of string)
    $result = preg_replace('/(<\?php\s+.*)$/is', '', $result);
    
    return $result;
}

/**
 * Generate a unique page filename
 * @param string $title Page title
 * @return string Safe filename
 */
function generatePageFilename($title) {
    $safe = preg_replace('/[^a-zA-Z0-9_-]/', '', str_replace(' ', '-', $title));
    return strtolower($safe) . '_' . substr(md5(time() . rand()), 0, 8) . '.php';
}

/**
 * Get list of user-created pages
 * @return array List of page info
 */
function getPageList() {
    $pages = array();
    $pagesDir = dirname(__DIR__) . '/pages/';
    
    if (is_dir($pagesDir)) {
        $files = glob($pagesDir . '*.php');
        foreach ($files as $file) {
            $content = file_get_contents($file);
            $title = basename($file, '.php');
            
            // Try to extract title from content
            if (preg_match('/<h1[^>]*>([^<]+)<\/h1>/i', $content, $m)) {
                $title = $m[1];
            }
            
            $pages[] = array(
                'filename' => basename($file),
                'title' => $title,
                'created' => filemtime($file)
            );
        }
    }
    
    return $pages;
}

/**
 * Delete a page
 * @param string $filename Page filename
 * @return bool Success status
 */
function deletePage($filename) {
    $pagesDir = dirname(__DIR__) . '/pages/';
    $filepath = $pagesDir . basename($filename);
    
    if (file_exists($filepath) && strpos(realpath($filepath), realpath($pagesDir)) === 0) {
        return unlink($filepath);
    }
    return false;
}
?>
