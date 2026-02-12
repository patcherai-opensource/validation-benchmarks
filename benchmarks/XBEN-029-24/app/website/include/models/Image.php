<?php

require_once(__DIR__ . '/FileUtils.php');

/**
 * Image
 *
 * The Image model handles saving uploaded images to the file system.
 */
class Image {

    /**
     * Save an image to the given path.
     *
     * @param string $path The target directory
     * @param string $name The file name (without extension)
     * @param string $extension The file extension
     * @param string $base64 The base64 encoded file content
     * @return array Response with success status and message
     */
    public static function save($path, $name, $extension, $base64) {
        $response = array('success' => false, 'error' => '');

        if (empty($name) || empty($extension) || empty($base64)) {
            $response['error'] = 'Missing required parameters.';
            return $response;
        }

        $allowedTypes = FileUtils::allowedFileTypes();
        $ext = strtolower(trim($extension));

        if (!in_array($ext, $allowedTypes)) {
            $response['error'] = 'File type "' . $ext . '" is not allowed. Permitted types: ' . implode(', ', $allowedTypes);
            return $response;
        }

        $sanitizedName = FileUtils::sanitizeFilename($name);
        
        if (empty($sanitizedName)) {
            $response['error'] = 'Invalid file name.';
            return $response;
        }

        $data = base64_decode($base64, true);

        if ($data === false) {
            $response['error'] = 'Invalid base64 data.';
            return $response;
        }

        $maxSize = defined('AM_MAX_UPLOAD_SIZE') ? AM_MAX_UPLOAD_SIZE : 10485760;

        if (strlen($data) > $maxSize) {
            $response['error'] = 'File exceeds maximum upload size.';
            return $response;
        }

        if (!is_dir($path)) {
            mkdir($path, 0755, true);
        }

        $filePath = rtrim($path, '/') . '/' . $sanitizedName . '.' . $ext;

        if (file_put_contents($filePath, $data) !== false) {
            $response['success'] = true;
            $response['file'] = $sanitizedName . '.' . $ext;
        } else {
            $response['error'] = 'Failed to write file to disk.';
        }

        return $response;
    }
}

?>
