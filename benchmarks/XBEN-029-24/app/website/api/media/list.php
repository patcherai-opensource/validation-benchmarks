<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

header('Content-Type: application/json');

require_once(__DIR__ . '/../../include/db_config.php');
require_once(__DIR__ . '/../../include/auth.php');

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(array("error" => "Method not allowed"));
    exit();
}

$files = array();
$result = mysqli_query($db_connect, "SELECT mf.id, mf.filename, mf.original_name, mf.file_type, mf.file_size, mf.created_at, u.username as uploader FROM media_files mf LEFT JOIN users u ON mf.uploaded_by = u.id ORDER BY mf.created_at DESC LIMIT 100");

if ($result) {
    while ($row = mysqli_fetch_assoc($result)) {
        $files[] = $row;
    }
}

echo json_encode(array("files" => $files));
?>
