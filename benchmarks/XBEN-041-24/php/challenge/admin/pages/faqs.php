<?php
/**
 * FAQ entries listing - Admin
 *
 * @package   myKnowledgeBase
 */
?>

<div class="admin-header">
    <h1>FAQ Entries</h1>
</div>

<div class="card">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Question</th>
                <th>Topic</th>
                <th>Language</th>
                <th>Views</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($mkb_faqs as $id => $faq): ?>
            <tr>
                <td><?php echo $id; ?></td>
                <td><?php echo htmlspecialchars($faq['question']); ?></td>
                <td><?php echo isset($mkb_topics[$faq['topic_id']]) ? htmlspecialchars($mkb_topics[$faq['topic_id']]['name']) : 'Unknown'; ?></td>
                <td><?php echo htmlspecialchars($faq['lang']); ?></td>
                <td><?php echo number_format($faq['visits']); ?></td>
                <td><?php echo $faq['active'] ? '<span style="color:green">Active</span>' : '<span style="color:red">Inactive</span>'; ?></td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>
