<?php

namespace App\Controller;

/**
 * Controller for managing product media files.
 * Handles upload and listing of product images and documents.
 */
class MediaController
{
    private array $config;

    public function __construct(array $config)
    {
        $this->config = $config;
    }

    /**
     * POST /api/rest/v1/media-files
     * Upload a new media file for product enrichment.
     */
    public function postAction(): void
    {
        header('Content-Type: application/json');

        if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
            http_response_code(400);
            echo json_encode([
                'code' => 400,
                'message' => 'No file was uploaded or an upload error occurred.',
            ]);
            return;
        }

        $file = $_FILES['file'];

        // Validate file size
        if ($file['size'] > $this->config['max_upload_size']) {
            http_response_code(422);
            echo json_encode([
                'code' => 422,
                'message' => 'The file is too large. Maximum size is 10MB.',
            ]);
            return;
        }

        // Validate MIME type using finfo
        $finfo = new \finfo(FILEINFO_MIME_TYPE);
        $detectedMime = $finfo->file($file['tmp_name']);

        if (!in_array($detectedMime, $this->config['allowed_mime_types'], true)) {
            http_response_code(422);
            echo json_encode([
                'code' => 422,
                'message' => sprintf(
                    'The file type "%s" is not allowed. Allowed types: %s',
                    $detectedMime,
                    implode(', ', $this->config['allowed_mime_types'])
                ),
            ]);
            return;
        }

        $mediaDir = $this->config['media_directory'];

        if (!is_dir($mediaDir)) {
            mkdir($mediaDir, 0755, true);
        }

        // Generate a storage path preserving the original filename
        $originalName = basename($file['name']);
        $storagePath = $mediaDir . '/' . $originalName;

        // Avoid overwriting existing files
        if (file_exists($storagePath)) {
            $pathInfo = pathinfo($originalName);
            $originalName = $pathInfo['filename'] . '_' . uniqid() . '.' . ($pathInfo['extension'] ?? '');
            $storagePath = $mediaDir . '/' . $originalName;
        }

        if (!move_uploaded_file($file['tmp_name'], $storagePath)) {
            http_response_code(500);
            echo json_encode([
                'code' => 500,
                'message' => 'An error occurred while saving the file.',
            ]);
            return;
        }

        $mediaUrl = '/media/catalog/' . $originalName;

        http_response_code(201);
        echo json_encode([
            'code' => 201,
            'message' => 'Media file uploaded successfully.',
            'data' => [
                'code' => $originalName,
                'original_filename' => $file['name'],
                'mime_type' => $detectedMime,
                'size' => $file['size'],
                '_links' => [
                    'download' => [
                        'href' => $mediaUrl,
                    ],
                ],
            ],
        ]);
    }

    /**
     * GET /api/rest/v1/media-files
     * List uploaded media files.
     */
    public function listAction(): void
    {
        header('Content-Type: application/json');

        $mediaDir = $this->config['media_directory'];
        $items = [];

        if (is_dir($mediaDir)) {
            $files = scandir($mediaDir);
            foreach ($files as $file) {
                if ($file === '.' || $file === '..') {
                    continue;
                }
                $fullPath = $mediaDir . '/' . $file;
                $items[] = [
                    'code' => $file,
                    'original_filename' => $file,
                    'mime_type' => mime_content_type($fullPath),
                    'size' => filesize($fullPath),
                    '_links' => [
                        'download' => [
                            'href' => '/media/catalog/' . $file,
                        ],
                    ],
                ];
            }
        }

        echo json_encode([
            '_embedded' => [
                'items' => $items,
            ],
            'items_count' => count($items),
        ]);
    }
}