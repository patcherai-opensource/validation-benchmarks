<?php $pageTitle = 'My Notes'; include __DIR__ . '/header.php'; ?>
<div class="admin-wrapper">
    <?php include __DIR__ . '/admin_sidebar.php'; ?>
    <div class="admin-main">
        <h1>My Notes</h1>
        <?php if (empty($notes)): ?>
        <div class="card">
            <p style="color: #666;">You don't have any notes yet.</p>
        </div>
        <?php else: ?>
        <?php foreach ($notes as $note): ?>
        <div class="card">
            <h3><?php echo htmlspecialchars($note['Title']); ?>
                <span class="badge badge-<?php echo $note['Classification'] === 'restricted' ? 'restricted' : 'internal'; ?>">
                    <?php echo htmlspecialchars($note['Classification']); ?>
                </span>
            </h3>
            <p style="margin-top: 8px;"><?php echo htmlspecialchars($note['Content']); ?></p>
            <p style="margin-top: 8px; font-size: 0.8rem; color: #999;">Created: <?php echo htmlspecialchars($note['Created']); ?></p>
        </div>
        <?php endforeach; ?>
        <?php endif; ?>
    </div>
</div>
<?php include __DIR__ . '/footer.php'; ?>