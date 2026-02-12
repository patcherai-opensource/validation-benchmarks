<?php $pageTitle = 'Profile'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<div class="navbar">
    <a href="/dashboard" class="brand">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="#fff">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
        </svg>
        <?= APP_NAME ?>
    </a>
    <nav>
        <a href="/dashboard">Dashboard</a>
        <a href="/profile" class="active">Profile</a>
        <a href="/settings">Settings</a>
    </nav>
    <div class="user-info">
        <div class="avatar"><?= strtoupper(substr($user['username'], 0, 1)) ?></div>
        <span><?= htmlspecialchars($user['display_name']) ?></span>
        <a href="/logout" class="btn btn-secondary" style="padding: 4px 12px; font-size: 13px;">Logout</a>
    </div>
</div>

<div class="container">
    <h1 style="margin-bottom: 24px;">User Profile</h1>

    <div class="card">
        <h2>Account Information</h2>
        <table>
            <tr><th style="width: 200px;">Username</th><td><?= htmlspecialchars($user['username']) ?></td></tr>
            <tr><th>Display Name</th><td><?= htmlspecialchars($user['display_name']) ?></td></tr>
            <tr><th>Email</th><td><?= htmlspecialchars($user['email']) ?></td></tr>
            <tr><th>Role</th><td><span class="badge badge-info"><?= htmlspecialchars($user['role']) ?></span></td></tr>
            <tr><th>Two-Factor Auth</th><td><?= $user['two_factor_enabled'] ? '<span class="badge badge-success">Enabled</span>' : '<span class="badge badge-warning">Disabled</span>' ?></td></tr>
            <tr><th>Account Created</th><td><?= htmlspecialchars($user['created_at']) ?></td></tr>
        </table>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
