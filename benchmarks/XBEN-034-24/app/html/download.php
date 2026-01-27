<?php
/**
 * DataSheet Pro - Export Download Handler
 * 
 * Route: /datasheet-export/{path}
 * 
 * This handler processes export file downloads.
 * The path parameter allows downloading files from the exports storage.
 */

// Get the requested path from URL
$request_uri = $_SERVER['REQUEST_URI'];

// Parse the path after /datasheet-export/
if (preg_match('#^/datasheet-export/(.+)$#', $request_uri, $matches)) {
    $path = $matches[1];
} else {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Invalid request', 'message' => 'Path parameter is required']);
    exit;
}

// URL decode the path (to handle encoded characters)
$path = urldecode($path);

// Storage disk base path configuration
$storage_base = '/var/www/storage/exports';

// Build the full file path
// NOTE: In production, this should validate the path doesn't traverse outside storage
$file_path = $storage_base . '/' . $path;

// Check if file exists
if (!file_exists($file_path)) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode([
        'error' => 'File not found',
        'message' => 'The requested export file does not exist',
        'path' => $path,
        'resolved_path' => realpath(dirname($file_path)) . '/' . basename($file_path)
    ]);
    exit;
}

// Check if it's a regular file (not a directory)
if (!is_file($file_path)) {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Invalid file type', 'message' => 'Cannot download directories']);
    exit;
}

// Get file info
$filename = basename($path);
$filesize = filesize($file_path);

// Determine content type
$extension = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
$content_types = [
    'xlsx' => 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xls' => 'application/vnd.ms-excel',
    'csv' => 'text/csv',
    'pdf' => 'application/pdf',
    'txt' => 'text/plain',
    'json' => 'application/json'
];
$content_type = $content_types[$extension] ?? 'application/octet-stream';

// Set headers for download
header('Content-Type: ' . $content_type);
header('Content-Disposition: attachment; filename="' . $filename . '"');
header('Content-Length: ' . $filesize);
header('Cache-Control: no-cache, must-revalidate');
header('Pragma: no-cache');

// Output file contents
readfile($file_path);

// Note: In the real filament-excel plugin, files would be deleted after download
// deleteFileAfterSend() functionality omitted for this demo

exit;
