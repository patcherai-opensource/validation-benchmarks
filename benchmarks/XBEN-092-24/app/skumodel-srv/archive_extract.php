<?php
header('Content-Type: application/json');
require_once 'Archive_Tar.php';
require_once 'ReadClass.php';

$response = [
    'status' => 'failure',
    'message' => 'No archive path provided.'
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $archivePath = isset($_POST['archive_path']) ? $_POST['archive_path'] : '';
    $destPath = isset($_POST['dest_path']) ? $_POST['dest_path'] : '/tmp/extracted/';
    
    if ($archivePath) {
        if (!file_exists($archivePath)) {
            $response['message'] = 'Archive file not found at: ' . $archivePath;
        } else {
            try {
                // Create Archive_Tar instance with the vulnerable version
                $tar = new Archive_Tar($archivePath);
                
                // Extract archive - this will process filenames including phar:// paths
                // CVE-2018-1000888: filenames starting with phar:// bypass validation
                // and trigger PHP's automatic object deserialization
                ob_start();
                $result = $tar->extract($destPath);
                $output = ob_get_clean();
                
                if (isset($result['error'])) {
                    $response['message'] = $result['error'];
                } else {
                    $response = [
                        'status' => 'success',
                        'message' => 'Archive extracted successfully.',
                        'files' => $result['files'] ?? [],
                        'output' => $output
                    ];
                }
            } catch (Exception $e) {
                $response['message'] = 'Extraction error: ' . $e->getMessage();
            }
        }
    }
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
