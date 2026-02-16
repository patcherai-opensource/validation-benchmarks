<?php include __DIR__ . '/_admin_header.php'; ?>
<div class="admin-content">
    <div class="cms-content-header">
        <h2>Settings</h2>
    </div>
    <div class="cms-content-body">
        <div class="settings-form">
            <div class="field">
                <label>Site Title</label>
                <input type="text" value="<?= htmlspecialchars($siteConfig['Title'] ?? '') ?>" disabled class="text">
            </div>
            <div class="field">
                <label>Tagline</label>
                <input type="text" value="<?= htmlspecialchars($siteConfig['Tagline'] ?? '') ?>" disabled class="text">
            </div>
            <div class="field">
                <label>Theme</label>
                <input type="text" value="<?= htmlspecialchars($siteConfig['Theme'] ?? '') ?>" disabled class="text">
            </div>
            <p class="info">Contact your system administrator to modify these settings.</p>
        </div>
    </div>
</div>
<?php include __DIR__ . '/_admin_footer.php'; ?>
