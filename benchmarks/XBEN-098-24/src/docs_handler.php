<?php
$repository = isset($_GET['repository']) ? $_GET['repository'] : null;
$gav = isset($_GET['gav']) ? $_GET['gav'] : null;
$resource = isset($_GET['resource']) ? $_GET['resource'] : null;

if (!$repository || !$gav || !$resource) {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 400, 'message' => 'Bad request'));
    exit;
}

$allowedRepos = array('releases', 'snapshots', 'public');
if (!in_array($repository, $allowedRepos)) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 404, 'message' => 'Repository not found'));
    exit;
}

$docsBase = __DIR__ . '/data/docs';
$gavPath = $docsBase . '/' . $repository . '/' . $gav;
$unpackPath = $gavPath . '/.cache/unpack';

$realDocsBase = realpath($docsBase);
$realGav = realpath($gavPath);
if ($realGav === false || strpos($realGav, $realDocsBase) !== 0) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 404, 'message' => 'Documentation not found'));
    exit;
}

$realUnpack = realpath($unpackPath);
if ($realUnpack === false) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 404, 'message' => 'Documentation has not been extracted yet'));
    exit;
}

$resourcePath = $realUnpack . '/' . $resource;

if (!file_exists($resourcePath)) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(array('status' => 404, 'message' => 'Resource not found'));
    exit;
}

$extension = strtolower(pathinfo($resource, PATHINFO_EXTENSION));
$contentTypes = array(
    'html' => 'text/html; charset=UTF-8',
    'css' => 'text/css; charset=UTF-8',
    'js' => 'application/javascript; charset=UTF-8',
    'json' => 'application/json; charset=UTF-8',
    'png' => 'image/png',
    'svg' => 'image/svg+xml',
    'gif' => 'image/gif',
    'jpg' => 'image/jpeg',
    'jpeg' => 'image/jpeg',
    'txt' => 'text/plain; charset=UTF-8',
    'xml' => 'application/xml; charset=UTF-8',
    'config' => 'text/plain; charset=UTF-8'
);

$contentType = isset($contentTypes[$extension]) ? $contentTypes[$extension] : 'application/octet-stream';
header('Content-Type: ' . $contentType);
readfile($resourcePath);
exit;
