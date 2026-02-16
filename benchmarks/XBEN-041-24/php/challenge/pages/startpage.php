<?php
/**
 * Start page - shows popular FAQs and topic overview
 *
 * @package   myKnowledgeBase
 */

if (!defined('MKB_ROOT_DIR')) {
    http_response_code(400);
    exit();
}

// Sort FAQs by visits for "Top Questions"
$sorted_faqs = $mkb_faqs;
uasort($sorted_faqs, function($a, $b) { return $b['visits'] - $a['visits']; });
$top_faqs = array_slice($sorted_faqs, 0, 5, true);

?>

<div class="row">
    <div class="col-main">
        <h1>Welcome to <?php echo htmlspecialchars($mkb_config['main.title']); ?></h1>
        <p class="subtitle">Find answers to frequently asked questions</p>

        <div class="search-box">
            <form action="/" method="get">
                <input type="hidden" name="action" value="search">
                <input type="text" name="q" placeholder="Search the knowledge base..." class="search-input">
                <button type="submit" class="btn btn-primary">Search</button>
            </form>
        </div>

        <h2>Browse Topics</h2>
        <div class="topic-grid">
            <?php foreach ($mkb_topics as $id => $topic): ?>
                <?php if ($topic['parent_id'] === 0 && $topic['active']): ?>
                <div class="topic-card">
                    <?php if (!empty($topic['image']) && file_exists(MKB_IMAGES_DIR . $topic['image'])): ?>
                        <img src="/images/<?php echo htmlspecialchars($topic['image']); ?>" class="topic-card-image" alt="">
                    <?php endif; ?>
                    <h3><a href="/?action=overview&topic=<?php echo $id; ?>"><?php echo htmlspecialchars($topic['name']); ?></a></h3>
                    <p><?php echo htmlspecialchars($topic['description']); ?></p>
                </div>
                <?php endif; ?>
            <?php endforeach; ?>
        </div>

        <h2>Top Questions</h2>
        <div class="faq-list">
            <?php foreach ($top_faqs as $faqId => $faq): ?>
                <?php if ($faq['active']): ?>
                <div class="faq-item">
                    <a href="/?action=faq&id=<?php echo $faqId; ?>"><?php echo htmlspecialchars($faq['question']); ?></a>
                    <span class="faq-visits"><?php echo number_format($faq['visits']); ?> views</span>
                </div>
                <?php endif; ?>
            <?php endforeach; ?>
        </div>
    </div>
</div>
