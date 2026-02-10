<?php
/**
 * Export file download handler
 * 
 * Endpoint for downloading exported files from WP Export Handler.
 * Access via: /wp-content/plugins/wp-export-handler/download.php?path=filename.xlsx
 */

$base_path = dirname(__FILE__) . '/../../uploads/exports';

if (!isset($_GET['path']) || empty($_GET['path'])) {
    http_response_code(400);
    header('Content-Type: text/plain');
    echo 'Missing path parameter';
    exit;
}

$path = $_GET['path'];

$file_path = $base_path . '/' . $path;

if (!file_exists($file_path) || !is_readable($file_path)) {
    http_response_code(404);
    header('Content-Type: text/plain');
    echo 'Export file not found';
    exit;
}

$filename = basename($path);

header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename="' . $filename . '"');
header('Content-Length: ' . filesize($file_path));
header('Cache-Control: no-cache, no-store, must-revalidate');
header('Pragma: no-cache');
header('Expires: 0');

readfile($file_path);
exit;
