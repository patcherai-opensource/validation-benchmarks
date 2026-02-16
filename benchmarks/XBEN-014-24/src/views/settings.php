<?php $pageTitle = 'Settings - SecurePortal'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<nav class="navbar">
    <a href="/dashboard" class="brand">SecurePortal</a>
    <div class="nav-links">
        <a href="/dashboard">Dashboard</a>
        <a href="/account/profile">Profile</a>
        <a href="/account/settings" class="active">Settings</a>
        <a href="/auth/signout">Sign Out</a>
    </div>
</nav>

<div class="container">
    <?php if ($message): ?>
        <div class="alert alert-<?= $message['type'] ?>"><?= htmlspecialchars($message['text']) ?></div>
    <?php endif; ?>

    <div class="card">
        <h2>Change Password</h2>
        <form method="POST" action="/account/settings" style="max-width: 400px;">
            <input type="hidden" name="action" value="change_password">
            <div class="form-group">
                <label for="current_password">Current Password</label>
                <input type="password" id="current_password" name="current_password" required>
            </div>
            <div class="form-group">
                <label for="new_password">New Password</label>
                <input type="password" id="new_password" name="new_password" required>
            </div>
            <div class="form-group">
                <label for="confirm_password">Confirm New Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <button type="submit" class="btn">Update Password</button>
        </form>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
