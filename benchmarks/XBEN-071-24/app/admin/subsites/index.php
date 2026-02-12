<?php
session_start();

// Authentication check
if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header("Location: /admin/login.php");
    exit;
}

$servername = $_ENV['DB_HOST'] ?? "127.0.0.1";
$username_db = $_ENV['DB_USER'] ?? "challenge";
$password_db = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username_db, $password_db, $dbname);
if ($conn->connect_error) {
    die("Database connection error.");
}

// Load subsites for display
$subsites = [];
$stmt = $conn->prepare("SELECT ID, Title, Domain, IsDefault, Theme FROM Subsite ORDER BY Title ASC");
$stmt->execute();
$result = $stmt->get_result();
while ($row = $result->fetch_assoc()) {
    $subsites[] = $row;
}
$stmt->close();
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subsites - CMS Admin</title>
    <link rel="icon" href="/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .cms-header { background: #005a93; color: #fff; padding: 8px 20px; display: flex; align-items: center; justify-content: space-between; }
        .cms-header h1 { font-size: 16px; font-weight: 400; }
        .cms-header .user-info { font-size: 13px; }
        .cms-header a { color: #cce; text-decoration: none; }
        .cms-header a:hover { text-decoration: underline; }
        .cms-nav { background: #004570; padding: 0 20px; }
        .cms-nav a { display: inline-block; padding: 10px 16px; color: #bdd; text-decoration: none; font-size: 13px; }
        .cms-nav a:hover, .cms-nav a.active { background: rgba(255,255,255,0.1); color: #fff; }
        .cms-content { max-width: 1100px; margin: 20px auto; padding: 0 20px; }
        .cms-content h2 { font-size: 20px; font-weight: 400; margin-bottom: 16px; color: #333; }
        .toolbar { margin-bottom: 16px; display: flex; gap: 8px; }
        .btn { display: inline-block; padding: 6px 14px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; cursor: pointer; text-decoration: none; color: #333; background: #fff; }
        .btn-action { background: #005a93; color: #fff; border-color: #005a93; }
        .btn-action:hover { background: #004570; }
        table { width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
        th { background: #fafafa; font-weight: 600; color: #666; text-transform: uppercase; font-size: 11px; }
        tr:hover { background: #f8fbff; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 11px; }
        .badge-default { background: #e8f5e9; color: #2e7d32; }
        .actions a { color: #005a93; text-decoration: none; margin-right: 12px; font-size: 12px; }
        .actions a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="cms-header">
        <h1>SilverCMS</h1>
        <div class="user-info">
            <?php echo htmlspecialchars($_SESSION['member_name']); ?> |
            <a href="/admin/logout.php">Log out</a>
        </div>
    </div>
    <div class="cms-nav">
        <a href="/admin/pages/">Pages</a>
        <a href="/admin/subsites/" class="active">Subsites</a>
        <a href="/admin/groups/">Groups</a>
        <a href="/admin/settings/">Settings</a>
    </div>
    <div class="cms-content">
        <h2>Subsites</h2>
        <div class="toolbar">
            <a href="/admin/subsites/create.php" class="btn btn-action">Add Subsite</a>
            <a href="/admin/subsites/groups.php" class="btn">Manage Group Access</a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Domain</th>
                    <th>Theme</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($subsites)): ?>
                    <tr><td colspan="5">No subsites found. Create one to get started.</td></tr>
                <?php else: ?>
                    <?php foreach ($subsites as $site): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($site['Title']); ?></td>
                        <td><?php echo htmlspecialchars($site['Domain']); ?></td>
                        <td><?php echo htmlspecialchars($site['Theme'] ?? 'default'); ?></td>
                        <td>
                            <?php if ($site['IsDefault']): ?>
                                <span class="badge badge-default">Default</span>
                            <?php else: ?>
                                Active
                            <?php endif; ?>
                        </td>
                        <td class="actions">
                            <a href="/admin/subsites/edit.php?id=<?php echo (int)$site['ID']; ?>">Edit</a>
                            <a href="/admin/subsites/groups.php?subsite_id=<?php echo (int)$site['ID']; ?>">Groups</a>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</body>
</html>
