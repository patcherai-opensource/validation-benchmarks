<?php $pageTitle = 'Profile - SecurePortal'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<nav class="navbar">
    <a href="/dashboard" class="brand">SecurePortal</a>
    <div class="nav-links">
        <a href="/dashboard">Dashboard</a>
        <a href="/account/profile" class="active">Profile</a>
        <a href="/account/settings">Settings</a>
        <a href="/auth/signout">Sign Out</a>
    </div>
</nav>

<div class="container">
    <div class="card">
        <h2>Account Profile</h2>
        <table>
            <tr>
                <th style="width: 200px;">Username</th>
                <td><?= htmlspecialchars($user['username']) ?></td>
            </tr>
            <tr>
                <th>Role</th>
                <td><span class="badge badge-<?= $user['role'] ?>"><?= htmlspecialchars($user['role']) ?></span></td>
            </tr>
            <tr>
                <th>MFA Status</th>
                <td>
                    <?php if ($user['mfa_enabled']): ?>
                        <span class="badge badge-enabled">Enabled</span>
                    <?php else: ?>
                        <span class="badge badge-disabled">Disabled</span>
                    <?php endif; ?>
                </td>
            </tr>
            <tr>
                <th>Account Created</th>
                <td><?= htmlspecialchars($user['created_at']) ?></td>
            </tr>
            <tr>
                <th>Last Login</th>
                <td><?= htmlspecialchars($user['last_login'] ?? 'Never') ?></td>
            </tr>
        </table>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
