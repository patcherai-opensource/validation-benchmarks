<?php
/**
 * Single FAQ display page
 *
 * @package   myKnowledgeBase
 */

if (!defined('MKB_ROOT_DIR')) {
    http_response_code(400);
    exit();
}

$faq_id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if ($faq_id > 0 && isset($mkb_faqs[$faq_id])):
    $faq = $mkb_faqs[$faq_id];
    $topic = $mkb_topics[$faq['topic_id']] ?? null;
?>

<nav class="breadcrumb">
    <a href="/">Home</a> &raquo;
    <?php if ($topic): ?>
        <a href="/?action=overview&topic=<?php echo $faq['topic_id']; ?>"><?php echo htmlspecialchars($topic['name']); ?></a> &raquo;
    <?php endif; ?>
    <span>FAQ #<?php echo $faq_id; ?></span>
</nav>

<article class="faq-article">
    <h1><?php echo htmlspecialchars($faq['question']); ?></h1>
    <div class="faq-meta">
        <span class="faq-views"><?php echo number_format($faq['visits']); ?> views</span>
        <?php if ($topic): ?>
            <span class="faq-topic">Topic: <?php echo htmlspecialchars($topic['name']); ?></span>
        <?php endif; ?>
    </div>
    <div class="faq-answer">
        <p><?php echo nl2br(htmlspecialchars($faq['answer'])); ?></p>
    </div>
</article>

<?php else: ?>

<h1>FAQ Not Found</h1>
<p>The requested FAQ entry could not be found. <a href="/">Return to the home page</a>.</p>

<?php endif; ?>
