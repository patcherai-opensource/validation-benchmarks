<?php $pageTitle = 'Dashboard - SecurePortal'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<nav class="navbar">
    <a href="/dashboard" class="brand">SecurePortal</a>
    <div class="nav-links">
        <a href="/dashboard" class="active">Dashboard</a>
        <a href="/account/profile">Profile</a>
        <a href="/account/settings">Settings</a>
        <a href="/auth/signout">Sign Out</a>
    </div>
</nav>

<div class="container">
    <h2 style="margin-bottom: 1.5rem;">Welcome, <?= htmlspecialchars($user['username']) ?>
        <span class="badge badge-<?= $user['role'] ?>"><?= htmlspecialchars($user['role']) ?></span>
    </h2>

    <?php if (!empty($notes)): ?>
    <div class="card">
        <h2>Secure Notes</h2>
        <?php foreach ($notes as $note): ?>
            <div style="margin-bottom: 1rem;">
                <strong><?= htmlspecialchars($note['title']) ?></strong>
                <span style="color: #999; font-size: 0.8rem;">&mdash; <?= htmlspecialchars($note['created_at']) ?></span>
                <div class="note-content"><?= htmlspecialchars($note['content']) ?></div>
            </div>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <?php if (!empty($auditLog)): ?>
    <div class="card">
        <h2>Recent Activity</h2>
        <table>
            <thead>
                <tr>
                    <th>Action</th>
                    <th>Details</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($auditLog as $entry): ?>
                <tr>
                    <td><?= htmlspecialchars($entry['action']) ?></td>
                    <td><?= htmlspecialchars($entry['details']) ?></td>
                    <td><?= htmlspecialchars($entry['created_at']) ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <?php endif; ?>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
