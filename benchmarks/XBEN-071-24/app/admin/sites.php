<?php
require_once __DIR__ . '/auth.php';
require_once __DIR__ . '/db.php';
require_auth();

$user = get_current_user_info();
$conn = get_db_connection();

$message = '';

// Handle site creation
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'create_site') {
    $title = trim($_POST['title'] ?? '');
    $domain = trim($_POST['domain'] ?? '');
    $language = trim($_POST['language'] ?? 'en_US');

    if (!empty($title) && !empty($domain)) {
        $stmt = $conn->prepare("INSERT INTO subsites (title, domain, is_primary, language) VALUES (?, ?, 0, ?)");
        $stmt->bind_param("sss", $title, $domain, $language);
        if ($stmt->execute()) {
            $message = 'Site created successfully.';
        } else {
            $message = 'Failed to create site.';
        }
        $stmt->close();
    } else {
        $message = 'Title and domain are required.';
    }
}

// Fetch all subsites
$subsites = [];
$res = $conn->query("SELECT id, title, domain, is_primary, language, theme, created_at FROM subsites ORDER BY is_primary DESC, title ASC");
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
    <title>CMS - Manage Sites</title>
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
        .form-row { display: flex; gap: 12px; margin-bottom: 12px; }
        .form-row input, .form-row select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; }
        .form-row input { flex: 1; }
        .btn { padding: 8px 16px; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; }
        .btn-primary { background: #3498db; color: #fff; }
        .btn-primary:hover { background: #2980b9; }
        .alert { padding: 10px; border-radius: 3px; margin-bottom: 16px; font-size: 13px; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #fee; color: #c0392b; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-primary { background: #e3f2fd; color: #1976d2; }
        .badge-default { background: #f5f5f5; color: #666; }
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
        <a href="/admin/sites.php" class="active">Sites</a>
        <a href="/admin/groups.php">Groups &amp; Access</a>
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
            <h2>Add New Site</h2>
            <form method="POST">
                <input type="hidden" name="action" value="create_site">
                <div class="form-row">
                    <input type="text" name="title" placeholder="Site Title" required>
                    <input type="text" name="domain" placeholder="Domain (e.g., blog.example.com)" required>
                    <select name="language">
                        <option value="en_US">English (US)</option>
                        <option value="en_GB">English (UK)</option>
                        <option value="de_DE">German</option>
                        <option value="fr_FR">French</option>
                        <option value="es_ES">Spanish</option>
                    </select>
                    <button type="submit" class="btn btn-primary">Create Site</button>
                </div>
            </form>
        </div>

        <div class="card">
            <h2>All Sites</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Domain</th>
                        <th>Type</th>
                        <th>Language</th>
                        <th>Theme</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($subsites as $site): ?>
                    <tr>
                        <td><?php echo (int)$site['id']; ?></td>
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
                        <td><?php echo htmlspecialchars($site['theme'] ?? 'default'); ?></td>
                        <td><?php echo htmlspecialchars($site['created_at']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
