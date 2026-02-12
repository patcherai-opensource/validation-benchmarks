<?php
require_once __DIR__ . '/config.php';

$collection = $_GET['collection'] ?? '';
$slug = $_GET['slug'] ?? '';
$db = getDB();

$stmt = $db->prepare("SELECT * FROM collections WHERE handle = ?");
$stmt->execute([$collection]);
$col = $stmt->fetch();

if (!$col) {
    http_response_code(404);
    echo renderLayout('Not Found', '<h1>Not Found</h1><p>The requested collection does not exist.</p>');
    exit;
}

$stmt = $db->prepare("SELECT * FROM entries WHERE collection_handle = ? AND slug = ?");
$stmt->execute([$collection, $slug]);
$entry = $stmt->fetch();

if (!$entry) {
    http_response_code(404);
    echo renderLayout('Not Found', '<h1>Entry Not Found</h1><p>The requested entry does not exist.</p>');
    exit;
}

$content = '<div class="breadcrumb"><a href="/">Home</a> / <a href="/collections/' . htmlspecialchars($collection) . '">' . htmlspecialchars($col['title']) . '</a> / ' . htmlspecialchars($entry['title']) . '</div>';
$content .= '<article class="card">';
$content .= '<h1>' . htmlspecialchars($entry['title']) . '</h1>';
$content .= '<div class="card-meta">By ' . htmlspecialchars($entry['author_name']) . ' &middot; ' . $entry['created_at'] . '</div>';

if ($entry['featured_image']) {
    $content .= '<img src="' . htmlspecialchars(ASSET_URL . $entry['featured_image']) . '" alt="" class="entry-image">';
}

$content .= '<div style="margin-top: 1rem;">' . nl2br(htmlspecialchars($entry['content'])) . '</div>';

if ($entry['attachment']) {
    $content .= '<div style="margin-top: 1rem;"><strong>Attachment:</strong> <a href="' . htmlspecialchars(ASSET_URL . $entry['attachment']) . '">' . htmlspecialchars($entry['attachment']) . '</a></div>';
}

$content .= '</article>';

if ($col['allow_uploads']) {
    $content .= '<div class="actions">';
    $content .= '<a href="/guest-entries/' . htmlspecialchars($collection) . '/' . htmlspecialchars($slug) . '/edit" class="btn btn-secondary">Edit Entry</a>';
    $content .= '</div>';
}

echo renderLayout($entry['title'], $content);
?>