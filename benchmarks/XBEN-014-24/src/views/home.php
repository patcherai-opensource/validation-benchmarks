<?php $pageTitle = 'SecurePortal - Enterprise Authentication'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<div class="auth-container">
    <div class="auth-card">
        <div class="logo">
            <h1>SecurePortal</h1>
            <p>Enterprise Authentication Gateway</p>
        </div>
        <p style="text-align: center; color: #666; margin-bottom: 1.5rem; font-size: 0.9rem;">
            Multi-factor authenticated access to your organization's resources.
        </p>
        <div style="text-align: center;">
            <a href="/auth/signin" class="btn">Sign In</a>
            <br><br>
            <a href="/help" style="color: #888; font-size: 0.85rem; text-decoration: none;">Documentation</a>
        </div>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
