<?php
/*
 * Serves raw javadoc files from the expanded javadoc archive.
 * Files are extracted to /var/reposilite/data/javadocs/{repository}/{gav}/
 *
 * The Location class handles path resolution for repository resources.
 */

$valid_repositories = ['releases', 'snapshots'];

if (!in_array($repository, $valid_repositories)) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(['status' => 404, 'message' => 'Repository not found']);
    exit;
}

// Resolve the javadoc unpack path for this artifact
$javadoc_base = '/var/reposilite/data/javadocs';
$gav_path = $repository . '/' . $gav;
$unpack_path = $javadoc_base . '/' . $gav_path;

// Resolve the requested resource within the javadoc directory
$resolved = $unpack_path . '/' . $resource;

if (!file_exists($resolved) || !is_file($resolved)) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(['status' => 404, 'message' => 'Resource not found']);
    exit;
}

// Determine content type
$ext = strtolower(pathinfo($resolved, PATHINFO_EXTENSION));
$content_types = [
    'html' => 'text/html',
    'css' => 'text/css',
    'js' => 'application/javascript',
    'png' => 'image/png',
    'jpg' => 'image/jpeg',
    'gif' => 'image/gif',
    'svg' => 'image/svg+xml',
    'txt' => 'text/plain',
    'xml' => 'application/xml',
    'json' => 'application/json',
];

$content_type = isset($content_types[$ext]) ? $content_types[$ext] : 'application/octet-stream';
header('Content-Type: ' . $content_type);

// Stream the file content
readfile($resolved);
exit;
