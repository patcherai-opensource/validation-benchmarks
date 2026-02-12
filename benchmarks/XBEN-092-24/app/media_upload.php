<?php

require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/auth.php';

use Twig\Loader\FilesystemLoader;
use Twig\Environment;

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader, [
    'charset' => 'UTF-8',
    'strict_variables' => false,
    'autoescape' => 'html',
]);

$session = requireAuth();
$db = include __DIR__ . '/database.php';

$message = '';
$messageType = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
    $file = $_FILES['file'];

    if ($file['error'] !== UPLOAD_ERR_OK) {
        $message = 'Upload failed. Please try again.';
        $messageType = 'error';
    } else {
        $maxSize = 5 * 1024 * 1024; // 5MB
        if ($file['size'] > $maxSize) {
            $message = 'File exceeds maximum size of 5MB.';
            $messageType = 'error';
        } else {
            // Check MIME type using finfo
            $finfo = new finfo(FILEINFO_MIME_TYPE);
            $detectedMime = $finfo->file($file['tmp_name']);

            $allowedMimeTypes = [
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/webp',
                'application/pdf',
                'application/octet-stream',
            ];

            if (!in_array($detectedMime, $allowedMimeTypes)) {
                $message = 'File type not allowed. Accepted: JPEG, PNG, GIF, WebP, PDF.';
                $messageType = 'error';
            } else {
                $originalName = basename($file['name']);

                // Generate storage path under media directory
                $hash = substr(md5(uniqid(mt_rand(), true)), 0, 8);
                $storageName = $hash . '_' . $originalName;
                $uploadDir = __DIR__ . '/media/product/';
                $storagePath = $uploadDir . $storageName;

                if (move_uploaded_file($file['tmp_name'], $storagePath)) {
                    $relativePath = '/media/product/' . $storageName;

                    $stmt = $db->prepare('INSERT INTO media_files (original_filename, file_path, mime_type, size, uploaded_by) VALUES (?, ?, ?, ?, ?)');
                    $stmt->execute([
                        $originalName,
                        $relativePath,
                        $detectedMime,
                        $file['size'],
                        $session['user_id'],
                    ]);

                    $message = 'File uploaded successfully.';
                    $messageType = 'success';
                } else {
                    $message = 'Failed to move uploaded file.';
                    $messageType = 'error';
                }
            }
        }
    }
}

$mediaFiles = $db->query('SELECT mf.*, u.username FROM media_files mf LEFT JOIN users u ON mf.uploaded_by = u.id ORDER BY mf.created_at DESC LIMIT 50')->fetchAll(PDO::FETCH_ASSOC);

echo $twig->render('media_upload.html.twig', [
    'user' => $session,
    'message' => $message,
    'message_type' => $messageType,
    'media_files' => $mediaFiles,
]);
