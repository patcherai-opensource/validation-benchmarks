<?php
require_once __DIR__ . '/config.php';

$db = getDB();

// Fetch collections with entry counts
$collections = $db->query("
    SELECT c.*, COUNT(e.id) as entry_count
    FROM collections c
    LEFT JOIN entries e ON e.collection_handle = c.handle AND e.status = 'published'
    GROUP BY c.id
    ORDER BY c.title
")->fetchAll();

// Fetch recent entries
$recentEntries = $db->query("
    SELECT e.*, c.title as collection_title
    FROM entries e
    JOIN collections c ON c.handle = e.collection_handle
    WHERE e.status = 'published'
    ORDER BY e.created_at DESC
    LIMIT 5
")->fetchAll();

$content = '<h1>Welcome to ' . APP_NAME . '</h1>';
$content .= '<p>A flat-file CMS powered by Statamic. Share your content with our community.</p>';

$content .= '<h2>Collections</h2>';
$content .= '<div class="collection-grid">';
foreach ($collections as $col) {
    $content .= '<div class="collection-card">';
    $content .= '<h3><a href="/collections/' . htmlspecialchars($col['handle']) . '">' . htmlspecialchars($col['title']) . '</a></h3>';
    $content .= '<p>' . htmlspecialchars($col['description']) . '</p>';
    $content .= '<p class="card-meta">' . $col['entry_count'] . ' entries</p>';
    if ($col['allow_uploads']) {
        $content .= '<a href="/guest-entries/' . htmlspecialchars($col['handle']) . '/create" class="btn">Submit Entry</a>';
    }
    $content .= '</div>';
}
$content .= '</div>';

$content .= '<h2 style="margin-top: 2rem;">Recent Entries</h2>';
foreach ($recentEntries as $entry) {
    $content .= '<div class="card">';
    $content .= '<div class="card-meta">' . htmlspecialchars($entry['collection_title']) . ' &middot; ' . htmlspecialchars($entry['author_name']) . ' &middot; ' . $entry['created_at'] . '</div>';
    $content .= '<h3><a href="/collections/' . htmlspecialchars($entry['collection_handle']) . '/' . htmlspecialchars($entry['slug']) . '">' . htmlspecialchars($entry['title']) . '</a></h3>';
    $content .= '<p>' . htmlspecialchars(substr($entry['content'], 0, 200)) . (strlen($entry['content']) > 200 ? '...' : '') . '</p>';
    $content .= '</div>';
}

echo renderLayout('Home', $content);
?>