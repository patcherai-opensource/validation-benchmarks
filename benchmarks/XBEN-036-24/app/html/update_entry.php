<?php
require_once __DIR__ . '/config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo renderLayout('Method Not Allowed', '<h1>Method Not Allowed</h1>');
    exit;
}

$collection = $_GET['collection'] ?? '';
$slug = $_GET['slug'] ?? '';
$db = getDB();

$stmt = $db->prepare("SELECT * FROM collections WHERE handle = ?");
$stmt->execute([$collection]);
$col = $stmt->fetch();

if (!$col || !$col['allow_uploads']) {
    http_response_code(403);
    echo renderLayout('Forbidden', '<h1>Not Allowed</h1>');
    exit;
}

$stmt = $db->prepare("SELECT * FROM entries WHERE collection_handle = ? AND slug = ?");
$stmt->execute([$collection, $slug]);
$entry = $stmt->fetch();

if (!$entry) {
    http_response_code(404);
    echo renderLayout('Not Found', '<h1>Entry Not Found</h1>');
    exit;
}

// Validate required fields
$title = trim($_POST['title'] ?? '');
$authorName = trim($_POST['author_name'] ?? '');
$authorEmail = trim($_POST['author_email'] ?? '');
$contentText = trim($_POST['content'] ?? '');

$errors = [];
if (empty($title)) $errors[] = 'Title is required.';
if (empty($authorName)) $errors[] = 'Author name is required.';
if (empty($authorEmail) || !filter_var($authorEmail, FILTER_VALIDATE_EMAIL)) $errors[] = 'A valid email address is required.';
if (empty($contentText)) $errors[] = 'Content is required.';

if (!empty($errors)) {
    $content = '<div class="alert alert-danger"><strong>Validation Error:</strong><ul>';
    foreach ($errors as $err) {
        $content .= '<li>' . htmlspecialchars($err) . '</li>';
    }
    $content .= '</ul></div>';
    $content .= '<a href="/guest-entries/' . htmlspecialchars($collection) . '/' . htmlspecialchars($slug) . '/edit" class="btn btn-secondary">Go Back</a>';
    echo renderLayout('Validation Error', $content);
    exit;
}

$featuredImage = $entry['featured_image'];
$attachment = $entry['attachment'];

// Process file uploads for asset fields
if (isset($_FILES['featured_image']) && $_FILES['featured_image']['error'] === UPLOAD_ERR_OK) {
    $featuredImage = uploadFile('featured_image');
}

if (isset($_FILES['attachment']) && $_FILES['attachment']['error'] === UPLOAD_ERR_OK) {
    $attachment = uploadFile('attachment');
}

$stmt = $db->prepare("
    UPDATE entries
    SET title = ?, content = ?, author_name = ?, author_email = ?, featured_image = ?, attachment = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
");
$stmt->execute([$title, $contentText, $authorName, $authorEmail, $featuredImage, $attachment, $entry['id']]);

$content = '<div class="alert alert-success">';
$content .= '<strong>Updated!</strong> Your changes have been saved.';
$content .= '</div>';

if ($featuredImage || $attachment) {
    $content .= '<div class="card"><h3>Attached Files</h3><ul>';
    if ($featuredImage) {
        $content .= '<li>Featured Image: <a href="' . htmlspecialchars(ASSET_URL . $featuredImage) . '">' . htmlspecialchars($featuredImage) . '</a></li>';
    }
    if ($attachment) {
        $content .= '<li>Attachment: <a href="' . htmlspecialchars(ASSET_URL . $attachment) . '">' . htmlspecialchars($attachment) . '</a></li>';
    }
    $content .= '</ul></div>';
}

$content .= '<a href="/collections/' . htmlspecialchars($collection) . '/' . htmlspecialchars($slug) . '" class="btn">View Entry</a>';

echo renderLayout('Entry Updated', $content);

/**
 * Handle file upload for an asset field.
 *
 * Processes the uploaded file and stores it in the configured
 * asset container directory.
 */
function uploadFile(string $key): ?string
{
    $file = $_FILES[$key];

    if ($file['error'] !== UPLOAD_ERR_OK) {
        return null;
    }

    if ($file['size'] > 10 * 1024 * 1024) {
        return null;
    }

    $originalName = basename($file['name']);
    $extension = pathinfo($originalName, PATHINFO_EXTENSION);
    $filename = uniqid() . '_' . preg_replace('/[^a-zA-Z0-9._-]/', '', $originalName);

    $uploadDir = UPLOAD_DIR;
    if (!is_dir($uploadDir)) {
        mkdir($uploadDir, 0755, true);
    }

    $destination = $uploadDir . $filename;

    if (move_uploaded_file($file['tmp_name'], $destination)) {
        return $filename;
    }

    return null;
}
?>
