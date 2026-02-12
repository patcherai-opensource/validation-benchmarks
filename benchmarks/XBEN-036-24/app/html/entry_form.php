<?php
require_once __DIR__ . '/config.php';

$collection = $_GET['collection'] ?? '';
$slug = $_GET['slug'] ?? null;
$db = getDB();

$stmt = $db->prepare("SELECT * FROM collections WHERE handle = ?");
$stmt->execute([$collection]);
$col = $stmt->fetch();

if (!$col) {
    http_response_code(404);
    echo renderLayout('Not Found', '<h1>Collection Not Found</h1><p>The requested collection does not exist.</p>');
    exit;
}

if (!$col['allow_uploads']) {
    http_response_code(403);
    echo renderLayout('Not Allowed', '<h1>Submissions Closed</h1><p>This collection does not accept guest submissions.</p>');
    exit;
}

$entry = null;
$isEdit = false;

if ($slug) {
    $stmt = $db->prepare("SELECT * FROM entries WHERE collection_handle = ? AND slug = ?");
    $stmt->execute([$collection, $slug]);
    $entry = $stmt->fetch();
    if (!$entry) {
        http_response_code(404);
        echo renderLayout('Not Found', '<h1>Entry Not Found</h1>');
        exit;
    }
    $isEdit = true;
}

$pageTitle = $isEdit ? 'Edit Entry' : 'Submit New Entry';
$actionUrl = $isEdit
    ? '/guest-entries/' . htmlspecialchars($collection) . '/' . htmlspecialchars($slug) . '/update'
    : '/guest-entries/' . htmlspecialchars($collection) . '/store';

$content = '<div class="breadcrumb"><a href="/">Home</a> / <a href="/collections/' . htmlspecialchars($collection) . '">' . htmlspecialchars($col['title']) . '</a> / ' . $pageTitle . '</div>';
$content .= '<h1>' . $pageTitle . '</h1>';
$content .= '<p>Submit your content to the <strong>' . htmlspecialchars($col['title']) . '</strong> collection.</p>';

$content .= '<form action="' . $actionUrl . '" method="POST" enctype="multipart/form-data" class="card">';

$content .= '<div class="form-group">';
$content .= '<label for="title">Title *</label>';
$content .= '<input type="text" id="title" name="title" required value="' . htmlspecialchars($entry['title'] ?? '') . '">';
$content .= '</div>';

$content .= '<div class="form-group">';
$content .= '<label for="author_name">Your Name *</label>';
$content .= '<input type="text" id="author_name" name="author_name" required value="' . htmlspecialchars($entry['author_name'] ?? '') . '">';
$content .= '</div>';

$content .= '<div class="form-group">';
$content .= '<label for="author_email">Email Address *</label>';
$content .= '<input type="email" id="author_email" name="author_email" required value="' . htmlspecialchars($entry['author_email'] ?? '') . '">';
$content .= '</div>';

$content .= '<div class="form-group">';
$content .= '<label for="content">Content *</label>';
$content .= '<textarea id="content" name="content" required>' . htmlspecialchars($entry['content'] ?? '') . '</textarea>';
$content .= '</div>';

$content .= '<div class="form-group">';
$content .= '<label for="featured_image">Featured Image</label>';
$content .= '<input type="file" id="featured_image" name="featured_image">';
if ($entry && $entry['featured_image']) {
    $content .= '<p class="form-hint">Current: ' . htmlspecialchars($entry['featured_image']) . '</p>';
}
$content .= '<p class="form-hint">Upload an image for your entry.</p>';
$content .= '</div>';

$content .= '<div class="form-group">';
$content .= '<label for="attachment">Attachment</label>';
$content .= '<input type="file" id="attachment" name="attachment">';
if ($entry && $entry['attachment']) {
    $content .= '<p class="form-hint">Current: ' . htmlspecialchars($entry['attachment']) . '</p>';
}
$content .= '<p class="form-hint">Attach a supporting document.</p>';
$content .= '</div>';

$content .= '<button type="submit" class="btn">' . ($isEdit ? 'Update Entry' : 'Submit Entry') . '</button>';
$content .= '</form>';

echo renderLayout($pageTitle . ' — ' . $col['title'], $content);
?>