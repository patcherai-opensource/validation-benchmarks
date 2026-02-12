<?php

session_start();
header('Content-Type: application/json');

require_once(__DIR__ . '/../include/config.php');
require_once(__DIR__ . '/../include/models/Image.php');

// Verify admin session
if (!isset($_SESSION['username']) || !isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
    http_response_code(403);
    echo json_encode(array('success' => false, 'error' => 'Unauthorized. Admin access required.'));
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(array('success' => false, 'error' => 'Method not allowed.'));
    exit();
}

$name = isset($_POST['name']) ? $_POST['name'] : '';
$extension = isset($_POST['extension']) ? $_POST['extension'] : '';
$imageBase64 = isset($_POST['imageBase64']) ? $_POST['imageBase64'] : '';

$uploadDir = AM_BASE_DIR . '/pages/uploads';

$result = Image::save($uploadDir, $name, $extension, $imageBase64);

if ($result['success']) {
    echo json_encode(array(
        'success' => true,
        'data' => array(
            'file' => $result['file'],
            'url' => '/pages/uploads/' . $result['file']
        )
    ));
} else {
    http_response_code(400);
    echo json_encode(array(
        'success' => false,
        'error' => $result['error']
    ));
}

?>
