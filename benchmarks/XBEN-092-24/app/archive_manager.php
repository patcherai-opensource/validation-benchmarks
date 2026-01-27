<?php

use Twig\Loader\FilesystemLoader;
use Twig\Environment;

require_once __DIR__ . '/vendor/autoload.php';

$loader = new FilesystemLoader(__DIR__ . '/templates');
$twig = new Environment($loader);

// Handle form submissions
$result = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = isset($_POST['action']) ? $_POST['action'] : '';
    
    if ($action === 'upload') {
        // Handle file upload - proxy to internal service
        if (isset($_FILES['archive']) && $_FILES['archive']['error'] === UPLOAD_ERR_OK) {
            $fileContent = file_get_contents($_FILES['archive']['tmp_name']);
            $base64Data = base64_encode($fileContent);
            
            // Send to internal service
            $postData = http_build_query(['data' => $base64Data]);
            $context = stream_context_create([
                'http' => [
                    'method' => 'POST',
                    'header' => 'Content-Type: application/x-www-form-urlencoded',
                    'content' => $postData
                ]
            ]);
            
            $response = @file_get_contents('http://skumodel:4455/asset_upload', false, $context);
            if ($response) {
                $result = json_decode($response, true);
            } else {
                $error = 'Failed to connect to archive service';
            }
        } else {
            $error = 'No file uploaded or upload error';
        }
    } elseif ($action === 'extract') {
        $archivePath = isset($_POST['archive_path']) ? $_POST['archive_path'] : '';
        
        if (!empty($archivePath)) {
            $postData = http_build_query(['archive_path' => $archivePath]);
            $context = stream_context_create([
                'http' => [
                    'method' => 'POST',
                    'header' => 'Content-Type: application/x-www-form-urlencoded',
                    'content' => $postData
                ]
            ]);
            
            $response = @file_get_contents('http://skumodel:4455/archive_extract', false, $context);
            if ($response) {
                $result = json_decode($response, true);
            } else {
                $error = 'Failed to connect to archive service';
            }
        } else {
            $error = 'Please provide archive path';
        }
    }
}

echo $twig->render('archive_manager.html.twig', [
    'result' => $result,
    'error' => $error
]);
?>
