<?php
session_start();

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

$groups = [];
$stmt = $conn->prepare("SELECT g.ID, g.Title, g.Code, g.SubsiteID, g.AccessAllSubsites FROM SecurityGroup g ORDER BY g.Title ASC");
$stmt->execute();
$result = $stmt->get_result();
while ($row = $result->fetch_assoc()) {
    $groups[] = $row;
}
$stmt->close();

// Load members per group
$memberCounts = [];
$result = $conn->query("SELECT GroupID, COUNT(*) as cnt FROM Group_Members GROUP BY GroupID");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $memberCounts[$row['GroupID']] = $row['cnt'];
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Groups - CMS Admin</title>
    <link rel="icon" href="/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .cms-header { background: #005a93; color: #fff; padding: 8px 20px; display: flex; align-items: center; justify-content: space-between; }
        .cms-header h1 { font-size: 16px; font-weight: 400; }
        .cms-header .user-info { font-size: 13px; }
        .cms-header a { color: #cce; text-decoration: none; }
        .cms-nav { background: #004570; padding: 0 20px; }
        .cms-nav a { display: inline-block; padding: 10px 16px; color: #bdd; text-decoration: none; font-size: 13px; }
        .cms-nav a:hover, .cms-nav a.active { background: rgba(255,255,255,0.1); color: #fff; }
        .cms-content { max-width: 1100px; margin: 20px auto; padding: 0 20px; }
        .cms-content h2 { font-size: 20px; font-weight: 400; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
        th { background: #fafafa; font-weight: 600; color: #666; text-transform: uppercase; font-size: 11px; }
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
        <a href="/admin/subsites/">Subsites</a>
        <a href="/admin/groups/" class="active">Groups</a>
        <a href="/admin/settings/">Settings</a>
    </div>
    <div class="cms-content">
        <h2>Security Groups</h2>
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Code</th>
                    <th>Members</th>
                    <th>Subsite ID</th>
                    <th>Access All Subsites</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($groups as $g): ?>
                <tr>
                    <td><?php echo htmlspecialchars($g['Title']); ?></td>
                    <td><code><?php echo htmlspecialchars($g['Code']); ?></code></td>
                    <td><?php echo (int)($memberCounts[$g['ID']] ?? 0); ?></td>
                    <td><?php echo (int)$g['SubsiteID']; ?></td>
                    <td><?php echo $g['AccessAllSubsites'] ? 'Yes' : 'No'; ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</body>
</html>
