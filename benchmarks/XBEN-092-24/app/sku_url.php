<?php

/**
 * Media Processing Gateway
 * Provides a web interface for uploading images and requesting format conversions
 * via the internal media processing service.
 */

class MediaGateway {
    private $serviceHost = 'skumodel';
    private $servicePort = 4455;

    public function uploadImage($fileData, $extension = 'jpg') {
        $postData = http_build_query([
            'data' => base64_encode($fileData),
            'extension' => $extension
        ]);
        return $this->sendRequest('/media_upload', $postData);
    }

    public function convertImage($sourcePath, $format = 'jpeg', $bgColor = '#FFFFFF') {
        $postData = http_build_query([
            'source_path' => $sourcePath,
            'format' => $format,
            'bg_color' => $bgColor
        ]);
        return $this->sendRequest('/media_convert', $postData);
    }

    private function sendRequest($endpoint, $postData) {
        $url = "http://{$this->serviceHost}:{$this->servicePort}{$endpoint}";
        $options = [
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/x-www-form-urlencoded',
                'content' => $postData,
                'timeout' => 10
            ]
        ];
        $context = stream_context_create($options);
        $response = @file_get_contents($url, false, $context);
        if ($response === FALSE) {
            return json_encode(['status' => 'error', 'message' => 'Service unavailable.']);
        }
        return $response;
    }
}

use Twig\Loader\FilesystemLoader;
use Twig\Environment;

require_once __DIR__ . '/vendor/autoload.php';

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader, [
    'autoescape' => 'html',
]);

$gateway = new MediaGateway();
$uploadResult = '';
$convertResult = '';
$action = isset($_POST['action']) ? $_POST['action'] : '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if ($action === 'upload' && isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
        $fileData = file_get_contents($_FILES['image']['tmp_name']);
        $ext = strtolower(pathinfo($_FILES['image']['name'], PATHINFO_EXTENSION));
        $uploadResult = $gateway->uploadImage($fileData, $ext);
    } elseif ($action === 'convert') {
        $sourcePath = isset($_POST['source_path']) ? trim($_POST['source_path']) : '';
        $format = isset($_POST['format']) ? trim($_POST['format']) : 'jpeg';
        $bgColor = isset($_POST['bg_color']) ? trim($_POST['bg_color']) : '#FFFFFF';
        $convertResult = $gateway->convertImage($sourcePath, $format, $bgColor);
    }
}

try {
    echo $twig->render('media_tools.html.twig', [
        'upload_result' => $uploadResult,
        'convert_result' => $convertResult,
        'action' => $action,
    ]);
} catch (\Exception $e) {
    echo 'An error occurred.';
}
