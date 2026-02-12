<?php
require_once __DIR__ . '/config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo renderLayout('Method Not Allowed', '<h1>Method Not Allowed</h1>');
    exit;
}

$collection = $_GET['collection'] ?? '';
$db = getDB();

$stmt = $db->prepare("SELECT * FROM collections WHERE handle = ?");
$stmt->execute([$collection]);
$col = $stmt->fetch();

if (!$col) {
    http_response_code(404);
    echo renderLayout('Not Found', '<h1>Collection Not Found</h1>');
    exit;
}

if (!$col['allow_uploads']) {
    http_response_code(403);
    echo renderLayout('Forbidden', '<h1>Submissions Closed</h1><p>This collection does not accept guest submissions.</p>');
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
    $content .= '<a href="/guest-entries/' . htmlspecialchars($collection) . '/create" class="btn btn-secondary">Go Back</a>';
    echo renderLayout('Validation Error', $content);
    exit;
}

$slug = generateSlug($title);

// Check for duplicate slug
$stmt = $db->prepare("SELECT id FROM entries WHERE collection_handle = ? AND slug = ?");
$stmt->execute([$collection, $slug]);
if ($stmt->fetch()) {
    $slug .= '-' . time();
}

$featuredImage = null;
$attachment = null;

// Process file uploads — handles asset fields
if (isset($_FILES['featured_image']) && $_FILES['featured_image']['error'] === UPLOAD_ERR_OK) {
    $featuredImage = uploadFile('featured_image');
}

if (isset($_FILES['attachment']) && $_FILES['attachment']['error'] === UPLOAD_ERR_OK) {
    $attachment = uploadFile('attachment');
}

// Store entry
$stmt = $db->prepare("
    INSERT INTO entries (collection_handle, title, slug, content, author_name, author_email, featured_image, attachment, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft')
");
$stmt->execute([$collection, $title, $slug, $contentText, $authorName, $authorEmail, $featuredImage, $attachment]);

$content = '<div class="alert alert-success">';
$content .= '<strong>Thank you!</strong> Your entry <em>' . htmlspecialchars($title) . '</em> has been submitted and will be reviewed shortly.';
$content .= '</div>';

if ($featuredImage || $attachment) {
    $content .= '<div class="card"><h3>Uploaded Files</h3><ul>';
    if ($featuredImage) {
        $content .= '<li>Featured Image: <a href="' . htmlspecialchars(ASSET_URL . $featuredImage) . '">' . htmlspecialchars($featuredImage) . '</a></li>';
    }
    if ($attachment) {
        $content .= '<li>Attachment: <a href="' . htmlspecialchars(ASSET_URL . $attachment) . '">' . htmlspecialchars($attachment) . '</a></li>';
    }
    $content .= '</ul></div>';
}

$content .= '<a href="/collections/' . htmlspecialchars($collection) . '" class="btn">Back to ' . htmlspecialchars($col['title']) . '</a>';

echo renderLayout('Entry Submitted', $content);

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

    // Validate file size (max 10MB)
    if ($file['size'] > 10 * 1024 * 1024) {
        return null;
    }

    // Generate a unique filename while preserving original extension
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
