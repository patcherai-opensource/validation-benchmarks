<?php $pageTitle = 'Admin'; include __DIR__ . '/header.php'; ?>
<div class="admin-wrapper">
    <?php include __DIR__ . '/admin_sidebar.php'; ?>
    <div class="admin-main">
        <h1>Dashboard</h1>
        <div class="card">
            <h3>Welcome, <?php echo htmlspecialchars($member['FirstName'] . ' ' . $member['Surname']); ?></h3>
            <p style="color: #666; margin-top: 8px;">Role: <?php echo htmlspecialchars(ucfirst(str_replace('-', ' ', $member['MemberGroup']))); ?></p>
        </div>
        <?php
        $db = SS_Database::getConn();
        $totalMembers = $db->querySingle("SELECT COUNT(*) FROM Member");
        $totalPages = 148;
        $totalNotes = $db->querySingle("SELECT COUNT(*) FROM AdminNote");
        ?>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number"><?php echo $totalMembers; ?></div>
                <div class="stat-label">Members</div>
            </div>
            <div class="stat-card">
                <div class="stat-number"><?php echo $totalPages; ?></div>
                <div class="stat-label">Pages</div>
            </div>
            <div class="stat-card">
                <div class="stat-number"><?php echo $totalNotes; ?></div>
                <div class="stat-label">Notes</div>
            </div>
        </div>
        <div class="card">
            <h3>Recent Activity</h3>
            <table>
                <tr><th>Time</th><th>Email</th><th>Status</th></tr>
                <?php
                $attempts = $db->query("SELECT * FROM LoginAttempt ORDER BY Created DESC LIMIT 10");
                while ($attempt = $attempts->fetchArray(SQLITE3_ASSOC)):
                ?>
                <tr>
                    <td><?php echo htmlspecialchars($attempt['Created']); ?></td>
                    <td><?php echo htmlspecialchars($attempt['Email']); ?></td>
                    <td><?php echo htmlspecialchars($attempt['Status']); ?></td>
                </tr>
                <?php endwhile; ?>
            </table>
        </div>
    </div>
</div>
<?php include __DIR__ . '/footer.php'; ?>