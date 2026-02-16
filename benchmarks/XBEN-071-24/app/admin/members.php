<?php
require_once __DIR__ . '/auth.php';
require_once __DIR__ . '/db.php';
require_auth();

$user = get_current_user_info();
$conn = get_db_connection();

$members = [];
$res = $conn->query("SELECT m.id, m.username, m.role, m.email, m.created_at,
    GROUP_CONCAT(g.title SEPARATOR ', ') as group_names
    FROM cms_members m
    LEFT JOIN member_groups mg ON m.id = mg.member_id
    LEFT JOIN access_groups g ON mg.group_id = g.id
    GROUP BY m.id ORDER BY m.username");
if ($res) {
    while ($row = $res->fetch_assoc()) {
        $members[] = $row;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMS - Members</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; }
        .topbar { background: #2c3e50; color: #fff; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }
        .topbar h1 { font-size: 16px; font-weight: 500; }
        .topbar a { color: #ecf0f1; text-decoration: none; margin-left: 16px; font-size: 13px; }
        .sidebar { position: fixed; left: 0; top: 44px; width: 220px; height: calc(100vh - 44px); background: #34495e; padding: 16px 0; }
        .sidebar a { display: block; padding: 10px 24px; color: #bdc3c7; text-decoration: none; font-size: 14px; }
        .sidebar a:hover, .sidebar a.active { background: #2c3e50; color: #ecf0f1; }
        .main { margin-left: 220px; padding: 24px; }
        .card { background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; }
        .card h2 { font-size: 18px; color: #333; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
        th { background: #f8f9fa; color: #555; font-weight: 500; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-admin { background: #fce4ec; color: #c62828; }
        .badge-editor { background: #e3f2fd; color: #1565c0; }
    </style>
</head>
<body>
    <div class="topbar">
        <h1>Multi-Site CMS Administration</h1>
        <div>
            <?php echo htmlspecialchars($user['username']); ?>
            <a href="/admin/logout.php">Sign Out</a>
        </div>
    </div>
    <div class="sidebar">
        <a href="/admin/index.php">Dashboard</a>
        <a href="/admin/sites.php">Sites</a>
        <a href="/admin/groups.php">Groups &amp; Access</a>
        <a href="/admin/members.php" class="active">Members</a>
        <a href="/admin/maintenance.php">Maintenance</a>
    </div>
    <div class="main">
        <div class="card">
            <h2>CMS Members</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Groups</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($members as $member): ?>
                    <tr>
                        <td><?php echo (int)$member['id']; ?></td>
                        <td><?php echo htmlspecialchars($member['username']); ?></td>
                        <td><?php echo htmlspecialchars($member['email']); ?></td>
                        <td>
                            <span class="badge <?php echo $member['role'] === 'administrator' ? 'badge-admin' : 'badge-editor'; ?>">
                                <?php echo htmlspecialchars($member['role']); ?>
                            </span>
                        </td>
                        <td><?php echo htmlspecialchars($member['group_names'] ?? 'None'); ?></td>
                        <td><?php echo htmlspecialchars($member['created_at']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
