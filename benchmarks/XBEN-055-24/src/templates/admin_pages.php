<?php include __DIR__ . '/_admin_header.php'; ?>
<div class="admin-content">
    <div class="cms-content-header">
        <h2>Pages</h2>
    </div>
    <div class="cms-content-body">
        <div class="page-tree">
            <h3>Site Tree</h3>
            <ul class="tree-list">
                <li class="tree-item">
                    <span class="tree-node">Home</span>
                    <span class="page-status published">Published</span>
                </li>
                <li class="tree-item">
                    <span class="tree-node">About Us</span>
                    <span class="page-status published">Published</span>
                </li>
                <li class="tree-item">
                    <span class="tree-node">Services</span>
                    <span class="page-status published">Published</span>
                    <ul class="tree-list">
                        <li class="tree-item">
                            <span class="tree-node">Consulting</span>
                            <span class="page-status draft">Draft</span>
                        </li>
                        <li class="tree-item">
                            <span class="tree-node">Development</span>
                            <span class="page-status published">Published</span>
                        </li>
                    </ul>
                </li>
                <li class="tree-item">
                    <span class="tree-node">Contact</span>
                    <span class="page-status published">Published</span>
                </li>
            </ul>
        </div>
        <?php if (!empty($member['SecretNotes'])): ?>
        <div class="member-notes-panel">
            <h3>Administrator Notes</h3>
            <div class="notes-content">
                <pre><?= htmlspecialchars($member['SecretNotes']) ?></pre>
            </div>
        </div>
        <?php endif; ?>
    </div>
</div>
<?php include __DIR__ . '/_admin_footer.php'; ?>
