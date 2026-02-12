<?php $pageTitle = '403 Forbidden'; ?>
<?php include __DIR__ . '/../layouts/header.php'; ?>

<div class="error-page">
    <h2>403 - Access Denied</h2>
    <p>You do not have permission to access this resource.</p>
    <p class="text-muted">This area is restricted to authorized internal network addresses only.</p>
    <p class="text-muted">Your IP address: <?= htmlspecialchars($ip ?? 'unknown') ?></p>
    <a href="/" class="btn btn-primary">Return to Home</a>
</div>

<?php include __DIR__ . '/../layouts/footer.php'; ?>
