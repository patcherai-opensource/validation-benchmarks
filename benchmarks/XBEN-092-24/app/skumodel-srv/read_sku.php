<?php
header('Content-Type: application/json');
require_once 'ReadClass.php';
require_once 'CacheManager.php';

$response = [
    'status' => 'error',
    'message' => 'Invalid request.'
];

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode($response);
    exit;
}

$src = isset($_POST['src']) ? $_POST['src'] : '';
$operation = isset($_POST['operation']) ? $_POST['operation'] : 'tojpg';
$width = isset($_POST['width']) ? (int)$_POST['width'] : 300;
$height = isset($_POST['height']) ? (int)$_POST['height'] : 200;
$quality = isset($_POST['quality']) ? (int)$_POST['quality'] : 80;

if (empty($src)) {
    $response['message'] = 'Missing required parameter: src';
    echo json_encode($response);
    exit;
}

$args = [];
switch ($operation) {
    case 'tojpg':
        $args = ['quality' => $quality];
        $result = ImageHelper::img_to_jpg($src, $quality);
        break;
    case 'resize':
        $args = ['width' => $width, 'height' => $height];
        $result = ImageHelper::resize($src, $width, $height);
        break;
    case 'towebp':
        $args = ['quality' => $quality];
        $result = ImageHelper::img_to_webp($src, $quality);
        break;
    case 'letterbox':
        $color = isset($_POST['color']) ? $_POST['color'] : '#000000';
        $args = ['width' => $width, 'height' => $height, 'color' => $color];
        $result = ImageHelper::letterbox($src, $width, $height, $color);
        break;
    default:
        $response['message'] = 'Unsupported operation: ' . htmlspecialchars($operation);
        echo json_encode($response);
        exit;
}

echo json_encode($result);
?>
