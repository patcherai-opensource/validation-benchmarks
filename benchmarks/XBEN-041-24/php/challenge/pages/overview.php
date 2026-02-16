<?php
/**
 * Topic overview / FAQ listing
 *
 * @package   myKnowledgeBase
 */

if (!defined('MKB_ROOT_DIR')) {
    http_response_code(400);
    exit();
}

$topic_id = isset($_GET['topic']) ? (int)$_GET['topic'] : 0;

?>

<?php if ($topic_id > 0 && isset($mkb_topics[$topic_id])): ?>
    <?php $topic = $mkb_topics[$topic_id]; ?>
    <h1><?php echo htmlspecialchars($topic['name']); ?></h1>
    <p><?php echo htmlspecialchars($topic['description']); ?></p>

    <?php if (!empty($topic['image']) && file_exists(MKB_IMAGES_DIR . $topic['image'])): ?>
        <img src="/images/<?php echo htmlspecialchars($topic['image']); ?>" class="topic-banner" alt="">
    <?php endif; ?>

    <div class="faq-list">
        <?php
        $found = false;
        foreach ($mkb_faqs as $id => $faq):
            if ($faq['topic_id'] == $topic_id && $faq['active']):
                $found = true;
        ?>
        <div class="faq-item">
            <a href="/?action=faq&id=<?php echo $id; ?>"><?php echo htmlspecialchars($faq['question']); ?></a>
            <span class="faq-visits"><?php echo number_format($faq['visits']); ?> views</span>
        </div>
        <?php
            endif;
        endforeach;
        if (!$found): ?>
            <p>No FAQ entries found for this topic.</p>
        <?php endif; ?>
    </div>

    <!-- Sub-topics -->
    <?php
    $sub_topics = array_filter($mkb_topics, function($t) use ($topic_id) {
        return $t['parent_id'] == $topic_id;
    });
    if (!empty($sub_topics)): ?>
        <h2>Sub-topics</h2>
        <div class="topic-grid">
            <?php foreach ($sub_topics as $subId => $sub): ?>
            <div class="topic-card">
                <h3><a href="/?action=overview&topic=<?php echo $subId; ?>"><?php echo htmlspecialchars($sub['name']); ?></a></h3>
                <p><?php echo htmlspecialchars($sub['description']); ?></p>
            </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>

<?php else: ?>
    <h1>All Topics</h1>
    <div class="topic-tree">
        <?php echo mkb_render_topic_tree($mkb_topics); ?>
    </div>
<?php endif; ?>
