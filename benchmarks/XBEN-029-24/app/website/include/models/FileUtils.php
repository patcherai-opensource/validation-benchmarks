<?php

/**
 * FileUtils
 *
 * Utility functions for file handling within the CMS.
 */
class FileUtils {

    /**
     * Return the array of allowed file types based on the AM_ALLOWED_FILE_TYPES constant.
     *
     * @return array The array of allowed file type extensions
     */
    public static function allowedFileTypes() {
        $types = AM_ALLOWED_FILE_TYPES;
        return array_map('trim', explode(',', strtolower($types)));
    }

    /**
     * Get the MIME type for a given extension.
     *
     * @param string $extension
     * @return string
     */
    public static function mimeType($extension) {
        $mimeTypes = array(
            'jpg'   => 'image/jpeg',
            'jpeg'  => 'image/jpeg',
            'png'   => 'image/png',
            'gif'   => 'image/gif',
            'svg'   => 'image/svg+xml',
            'webp'  => 'image/webp',
            'bmp'   => 'image/bmp',
            'ico'   => 'image/x-icon',
            'avif'  => 'image/avif',
            'phtml' => 'text/html'
        );

        $ext = strtolower($extension);

        if (isset($mimeTypes[$ext])) {
            return $mimeTypes[$ext];
        }

        return 'application/octet-stream';
    }

    /**
     * Sanitize a filename to prevent directory traversal.
     *
     * @param string $name
     * @return string
     */
    public static function sanitizeFilename($name) {
        $name = basename($name);
        $name = preg_replace('/[^a-zA-Z0-9_\-]/', '_', $name);
        return $name;
    }
}

?>
