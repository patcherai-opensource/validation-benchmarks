<?php
require_once __DIR__ . '/auth.php';
require_once __DIR__ . '/db.php';
require_auth();

$user = get_current_user_info();
$conn = get_db_connection();

$message = '';

// Handle group creation
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'create_group') {
    $title = trim($_POST['title'] ?? '');
    $access_all = isset($_POST['access_all_sites']) ? 1 : 0;

    if (!empty($title)) {
        $stmt = $conn->prepare("INSERT INTO access_groups (title, access_all_sites) VALUES (?, ?)");
        $stmt->bind_param("si", $title, $access_all);
        if ($stmt->execute()) {
            $group_id = $conn->insert_id;

            // Link to specific subsites if not global access
            if (!$access_all && !empty($_POST['site_ids'])) {
                foreach ($_POST['site_ids'] as $site_id) {
                    $sid = (int)$site_id;
                    $stmt2 = $conn->prepare("INSERT INTO group_subsites (group_id, subsite_id) VALUES (?, ?)");
                    $stmt2->bind_param("ii", $group_id, $sid);
                    $stmt2->execute();
                    $stmt2->close();
                }
            }
            $message = 'Group created successfully.';
        } else {
            $message = 'Failed to create group.';
        }
        $stmt->close();
    } else {
        $message = 'Group title is required.';
    }
}

// Fetch groups with subsite assignments
$groups = [];
$res = $conn->query("SELECT g.id, g.title, g.access_all_sites, g.created_at,
    GROUP_CONCAT(s.title SEPARATOR ', ') as site_names
    FROM access_groups g
    LEFT JOIN group_subsites gs ON g.id = gs.group_id
    LEFT JOIN subsites s ON gs.subsite_id = s.id
    GROUP BY g.id ORDER BY g.title");
if ($res) {
    while ($row = $res->fetch_assoc()) {
        $groups[] = $row;
    }
}

// Fetch subsites for the form
$subsites = [];
$res = $conn->query("SELECT id, title FROM subsites WHERE is_primary = 0 ORDER BY title");
if ($res) {
    while ($row = $res->fetch_assoc()) {
        $subsites[] = $row;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMS - Groups &amp; Access</title>
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
        .card { background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .card h2 { font-size: 18px; color: #333; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
        th { background: #f8f9fa; color: #555; font-weight: 500; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 13px; color: #555; margin-bottom: 4px; font-weight: 500; }
        .form-group input, .form-group select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; width: 100%; max-width: 400px; }
        .checkbox-group { display: flex; flex-wrap: wrap; gap: 8px; }
        .checkbox-group label { font-weight: normal; display: flex; align-items: center; gap: 4px; }
        .btn { padding: 8px 16px; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; }
        .btn-primary { background: #3498db; color: #fff; }
        .alert { padding: 10px; border-radius: 3px; margin-bottom: 16px; font-size: 13px; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #fee; color: #c0392b; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-global { background: #fff3e0; color: #e65100; }
        .badge-scoped { background: #e8f5e9; color: #2e7d32; }
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
        <a href="/admin/groups.php" class="active">Groups &amp; Access</a>
        <a href="/admin/members.php">Members</a>
        <a href="/admin/maintenance.php">Maintenance</a>
    </div>
    <div class="main">
        <?php if ($message): ?>
            <div class="alert <?php echo strpos($message, 'successfully') !== false ? 'alert-success' : 'alert-error'; ?>">
                <?php echo htmlspecialchars($message); ?>
            </div>
        <?php endif; ?>

        <div class="card">
            <h2>Create Access Group</h2>
            <form method="POST">
                <input type="hidden" name="action" value="create_group">
                <div class="form-group">
                    <label>Group Title</label>
                    <input type="text" name="title" required placeholder="e.g., Content Editors">
                </div>
                <div class="form-group">
                    <label><input type="checkbox" name="access_all_sites" value="1"> Access All Sites (Global Group)</label>
                </div>
                <div class="form-group">
                    <label>Or assign to specific sites:</label>
                    <div class="checkbox-group">
                        <?php foreach ($subsites as $site): ?>
                            <label>
                                <input type="checkbox" name="site_ids[]" value="<?php echo (int)$site['id']; ?>">
                                <?php echo htmlspecialchars($site['title']); ?>
                            </label>
                        <?php endforeach; ?>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">Create Group</button>
            </form>
        </div>

        <div class="card">
            <h2>Access Groups</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Access</th>
                        <th>Assigned Sites</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($groups as $group): ?>
                    <tr>
                        <td><?php echo (int)$group['id']; ?></td>
                        <td><?php echo htmlspecialchars($group['title']); ?></td>
                        <td>
                            <?php if ($group['access_all_sites']): ?>
                                <span class="badge badge-global">Global</span>
                            <?php else: ?>
                                <span class="badge badge-scoped">Scoped</span>
                            <?php endif; ?>
                        </td>
                        <td><?php echo htmlspecialchars($group['site_names'] ?? 'All Sites'); ?></td>
                        <td><?php echo htmlspecialchars($group['created_at']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
