<?php include __DIR__ . '/_admin_header.php'; ?>
<div class="admin-content">
    <div class="cms-content-header">
        <h2>Security</h2>
    </div>
    <div class="cms-content-body">
        <h3>Members</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Group</th>
                    <th>Last Visited</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($members as $m): ?>
                <tr>
                    <td><?= htmlspecialchars($m['FirstName'] . ' ' . $m['Surname']) ?></td>
                    <td><?= htmlspecialchars($m['Email']) ?></td>
                    <td><?= htmlspecialchars($m['GroupTitle'] ?? 'N/A') ?></td>
                    <td><?= htmlspecialchars($m['LastVisited'] ?? 'Never') ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <h3>Recent Login Attempts</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Email</th>
                    <th>Status</th>
                    <th>IP</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($loginAttempts as $attempt): ?>
                <tr>
                    <td><?= htmlspecialchars($attempt['Email']) ?></td>
                    <td class="status-<?= strtolower($attempt['Status']) ?>"><?= htmlspecialchars($attempt['Status']) ?></td>
                    <td><?= htmlspecialchars($attempt['IP']) ?></td>
                    <td><?= htmlspecialchars($attempt['Created']) ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
<?php include __DIR__ . '/_admin_footer.php'; ?>
