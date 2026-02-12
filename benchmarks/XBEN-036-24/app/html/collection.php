<?php
require_once __DIR__ . '/config.php';

$handle = $_GET['handle'] ?? '';
$db = getDB();

$stmt = $db->prepare("SELECT * FROM collections WHERE handle = ?");
$stmt->execute([$handle]);
$collection = $stmt->fetch();

if (!$collection) {
    http_response_code(404);
    echo renderLayout('Not Found', '<h1>Collection Not Found</h1><p>The requested collection does not exist.</p>');
    exit;
}

$stmt = $db->prepare("
    SELECT * FROM entries
    WHERE collection_handle = ? AND status = 'published'
    ORDER BY created_at DESC
");
$stmt->execute([$handle]);
$entries = $stmt->fetchAll();

$content = '<div class="breadcrumb"><a href="/">Home</a> / ' . htmlspecialchars($collection['title']) . '</div>';
$content .= '<h1>' . htmlspecialchars($collection['title']) . '</h1>';
$content .= '<p>' . htmlspecialchars($collection['description']) . '</p>';

if ($collection['allow_uploads']) {
    $content .= '<div style="margin: 1rem 0;"><a href="/guest-entries/' . htmlspecialchars($handle) . '/create" class="btn">Submit New Entry</a></div>';
}

if (empty($entries)) {
    $content .= '<p>No entries yet. Be the first to contribute!</p>';
} else {
    foreach ($entries as $entry) {
        $content .= '<div class="card">';
        $content .= '<div class="card-meta">' . htmlspecialchars($entry['author_name']) . ' &middot; ' . $entry['created_at'] . '</div>';
        $content .= '<h3><a href="/collections/' . htmlspecialchars($handle) . '/' . htmlspecialchars($entry['slug']) . '">' . htmlspecialchars($entry['title']) . '</a></h3>';
        $content .= '<p>' . htmlspecialchars(substr($entry['content'], 0, 300)) . (strlen($entry['content']) > 300 ? '...' : '') . '</p>';
        $content .= '</div>';
    }
}

echo renderLayout($collection['title'], $content);
?>