<?php
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');
error_reporting(0);

include("./include/db_config.php");

session_start();

$username = '';

if (isset($_SESSION['username'])){
    $username = $_SESSION['username'];
}

if(!$username){
    header("Location: index.php?error=failed_login");
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header("Location: dashboard.php");
    exit();
}

if (!isset($_FILES['image']) || $_FILES['image']['error'] !== UPLOAD_ERR_OK) {
    echo "Error: No file uploaded or upload error.";
    exit();
}

if (!isset($_POST['category_id']) || !isset($_POST['lang'])) {
    echo "Error: Missing required parameters.";
    exit();
}

$categoryId = intval($_POST['category_id']);
$categoryLang = $_POST['lang'];

$stmt = $db_connect->prepare("SELECT id FROM categories WHERE id = ?");
$stmt->bind_param("i", $categoryId);
$stmt->execute();
$result = $stmt->get_result();
if ($result->num_rows === 0) {
    echo "Error: Invalid category.";
    exit();
}

require_once './include/CategoryImage.php';

$categoryImage = new CategoryImage();
$categoryImage->setUploadedFile($_FILES['image']);

$uploadDir = './images/';
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}

$fileName = $categoryImage->getFileName($categoryId, $categoryLang);
$destPath = $uploadDir . $fileName;

if ($categoryImage->upload($destPath)) {
    echo "Image uploaded successfully: " . htmlspecialchars($fileName);
    
    $stmt = $db_connect->prepare("UPDATE categories SET lang = ? WHERE id = ?");
    $stmt->bind_param("si", $categoryLang, $categoryId);
    $stmt->execute();
} else {
    echo "Error: Failed to upload image.";
}
?>
