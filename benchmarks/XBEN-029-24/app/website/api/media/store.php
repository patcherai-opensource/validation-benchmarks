<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

header('Content-Type: application/json');

require_once(__DIR__ . '/../../include/db_config.php');
require_once(__DIR__ . '/../../include/auth.php');
require_once(__DIR__ . '/../../include/config.php');

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(array("error" => "Method not allowed"));
    exit();
}

$input = json_decode(file_get_contents('php://input'), true);

if (!$input) {
    $input = $_POST;
}

$csrfToken = isset($input['__csrf__']) ? $input['__csrf__'] : '';
if (!verifyCsrfToken($csrfToken)) {
    http_response_code(403);
    echo json_encode(array("error" => "Invalid session token"));
    exit();
}

$name = isset($input['name']) ? $input['name'] : '';
$extension = isset($input['extension']) ? strtolower(trim($input['extension'])) : '';
$fileData = isset($input['fileData']) ? $input['fileData'] : '';

if (empty($name) || empty($extension) || empty($fileData)) {
    http_response_code(400);
    echo json_encode(array("error" => "Missing required fields: name, extension, fileData"));
    exit();
}

$allowedTypes = getAllowedFileTypes();

if (!in_array($extension, $allowedTypes)) {
    http_response_code(406);
    echo json_encode(array("error" => "Unsupported file type: \"" . $extension . "\""));
    exit();
}

$data = preg_replace('/^data:[a-zA-Z0-9\/\+\-]+;base64,/', '', $fileData);
$data = base64_decode($data);

if ($data === false) {
    http_response_code(400);
    echo json_encode(array("error" => "Invalid file data encoding"));
    exit();
}

$safeName = preg_replace('/[^a-zA-Z0-9_\-]/', '', $name);
if (empty($safeName)) {
    $safeName = 'file_' . time();
}

$uploadDir = __DIR__ . '/../../media/uploads/';

if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0775, true);
}

$filename = $safeName . '.' . $extension;
$filepath = $uploadDir . $filename;

if (file_exists($filepath)) {
    $safeName = $safeName . '_' . substr(md5(time()), 0, 6);
    $filename = $safeName . '.' . $extension;
    $filepath = $uploadDir . $filename;
}

if (file_put_contents($filepath, $data) === false) {
    http_response_code(500);
    echo json_encode(array("error" => "Failed to save file"));
    exit();
}

$userId = $_SESSION['user_id'];
$fileSize = strlen($data);
$stmt = mysqli_prepare($db_connect, "INSERT INTO media_files (filename, original_name, file_type, file_size, uploaded_by) VALUES (?, ?, ?, ?, ?)");
mysqli_stmt_bind_param($stmt, "sssii", $filename, $name, $extension, $fileSize, $userId);
mysqli_stmt_execute($stmt);

echo json_encode(array(
    "success" => true,
    "filename" => $filename,
    "path" => "/media/uploads/" . $filename,
    "size" => $fileSize
));
?>
