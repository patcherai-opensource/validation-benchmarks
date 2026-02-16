<?php
require_once __DIR__ . '/auth.php';
require_once __DIR__ . '/db.php';
require_auth();

$user = get_current_user_info();
$conn = get_db_connection();

// Fetch subsites
$subsites = [];
$res = $conn->query("SELECT id, title, domain, is_primary, language, created_at FROM subsites ORDER BY is_primary DESC, title ASC");
if ($res) {
    while ($row = $res->fetch_assoc()) {
        $subsites[] = $row;
    }
}

// Fetch groups count
$group_count = 0;
$res = $conn->query("SELECT COUNT(*) as cnt FROM access_groups");
if ($res) {
    $row = $res->fetch_assoc();
    $group_count = $row['cnt'];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMS - Site Administration</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; }
        .topbar { background: #2c3e50; color: #fff; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }
        .topbar h1 { font-size: 16px; font-weight: 500; }
        .topbar .user-info { font-size: 13px; }
        .topbar a { color: #ecf0f1; text-decoration: none; margin-left: 16px; font-size: 13px; }
        .sidebar { position: fixed; left: 0; top: 44px; width: 220px; height: calc(100vh - 44px); background: #34495e; padding: 16px 0; }
        .sidebar a { display: block; padding: 10px 24px; color: #bdc3c7; text-decoration: none; font-size: 14px; }
        .sidebar a:hover, .sidebar a.active { background: #2c3e50; color: #ecf0f1; }
        .main { margin-left: 220px; padding: 24px; }
        .card { background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .card h2 { font-size: 18px; color: #333; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
        th { background: #f8f9fa; color: #555; font-weight: 500; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 500; }
        .badge-primary { background: #e3f2fd; color: #1976d2; }
        .badge-default { background: #f5f5f5; color: #666; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; text-align: center; }
        .stat-card .number { font-size: 32px; font-weight: 600; color: #2c3e50; }
        .stat-card .label { font-size: 13px; color: #777; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="topbar">
        <h1>Multi-Site CMS Administration</h1>
        <div class="user-info">
            <?php echo htmlspecialchars($user['username']); ?> (<?php echo htmlspecialchars($user['role']); ?>)
            <a href="/admin/logout.php">Sign Out</a>
        </div>
    </div>
    <div class="sidebar">
        <a href="/admin/index.php" class="active">Dashboard</a>
        <a href="/admin/sites.php">Sites</a>
        <a href="/admin/groups.php">Groups &amp; Access</a>
        <a href="/admin/members.php">Members</a>
        <a href="/admin/maintenance.php">Maintenance</a>
    </div>
    <div class="main">
        <div class="stats">
            <div class="stat-card">
                <div class="number"><?php echo count($subsites); ?></div>
                <div class="label">Active Sites</div>
            </div>
            <div class="stat-card">
                <div class="number"><?php echo $group_count; ?></div>
                <div class="label">Access Groups</div>
            </div>
            <div class="stat-card">
                <div class="number"><?php echo htmlspecialchars($user['role']); ?></div>
                <div class="label">Your Role</div>
            </div>
        </div>

        <div class="card">
            <h2>Sites Overview</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Domain</th>
                        <th>Type</th>
                        <th>Language</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($subsites as $site): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($site['id']); ?></td>
                        <td><?php echo htmlspecialchars($site['title']); ?></td>
                        <td><?php echo htmlspecialchars($site['domain']); ?></td>
                        <td>
                            <?php if ($site['is_primary']): ?>
                                <span class="badge badge-primary">Primary</span>
                            <?php else: ?>
                                <span class="badge badge-default">Subsite</span>
                            <?php endif; ?>
                        </td>
                        <td><?php echo htmlspecialchars($site['language']); ?></td>
                        <td><?php echo htmlspecialchars($site['created_at']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
