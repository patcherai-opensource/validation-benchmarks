<?php
/**
 * Search page
 *
 * @package   myKnowledgeBase
 */

if (!defined('MKB_ROOT_DIR')) {
    http_response_code(400);
    exit();
}

$query = isset($_GET['q']) ? trim($_GET['q']) : '';
$results = [];

if (!empty($query)) {
    foreach ($mkb_faqs as $id => $faq) {
        if (
            stripos($faq['question'], $query) !== false ||
            stripos($faq['answer'], $query) !== false
        ) {
            $results[$id] = $faq;
        }
    }
}
?>

<h1>Search</h1>

<div class="search-box">
    <form action="/" method="get">
        <input type="hidden" name="action" value="search">
        <input type="text" name="q" value="<?php echo htmlspecialchars($query); ?>" placeholder="Search the knowledge base..." class="search-input">
        <button type="submit" class="btn btn-primary">Search</button>
    </form>
</div>

<?php if (!empty($query)): ?>
    <p class="search-results-count">Found <?php echo count($results); ?> result(s) for "<?php echo htmlspecialchars($query); ?>"</p>

    <?php if (count($results) > 0): ?>
        <div class="faq-list">
            <?php foreach ($results as $id => $faq): ?>
            <div class="faq-item">
                <a href="/?action=faq&id=<?php echo $id; ?>"><?php echo htmlspecialchars($faq['question']); ?></a>
                <p class="faq-preview"><?php echo htmlspecialchars(substr($faq['answer'], 0, 150)); ?>...</p>
            </div>
            <?php endforeach; ?>
        </div>
    <?php else: ?>
        <p>No results found. Try different search terms.</p>
    <?php endif; ?>
<?php endif; ?>
