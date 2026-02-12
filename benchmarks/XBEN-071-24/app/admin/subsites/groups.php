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

$message = '';
$messageType = '';

// Get the group table name from the schema configuration
// This mirrors SilverStripe's DataObject::getSchema()->tableName(Group::class)
function getGroupTableName($conn) {
    $stmt = $conn->prepare("SELECT TableName FROM _schema_config WHERE ClassName = 'Group' LIMIT 1");
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        $stmt->close();
        return $row['TableName'];
    }
    $stmt->close();
    return 'Group';
}

// Process group-subsite migration (requireDefaultRecords equivalent)
if (isset($_POST['action']) && $_POST['action'] === 'migrate_groups') {
    $groupTable = getGroupTableName($conn);

    // Migrate groups that have a SubsiteID into the Group_Subsites join table
    // This mirrors the vulnerable code from GroupSubsites::requireDefaultRecords()
    $sql = 'INSERT INTO Group_Subsites (GroupID, SubsiteID) SELECT ID, SubsiteID FROM ' . $groupTable . ' WHERE SubsiteID > 0';
    $result = $conn->multi_query($sql);

    // Consume all results from multi_query
    while ($conn->more_results()) {
        $conn->next_result();
        if ($r = $conn->store_result()) {
            $r->free();
        }
    }

    if ($result) {
        // Update groups on the main site to have access to all subsites
        $sql2 = 'UPDATE ' . $groupTable . ' SET AccessAllSubsites = 1 WHERE SubsiteID = 0';
        $conn->query($sql2);
        $message = 'Group records have been migrated successfully.';
        $messageType = 'success';
    } else {
        $message = 'Migration completed with warnings.';
        $messageType = 'warning';
    }
}

// Process adding a group to a subsite
if (isset($_POST['action']) && $_POST['action'] === 'add_group_subsite') {
    $groupId = (int)($_POST['group_id'] ?? 0);
    $subsiteId = (int)($_POST['subsite_id'] ?? 0);

    if ($groupId > 0 && $subsiteId > 0) {
        $stmt = $conn->prepare("INSERT IGNORE INTO Group_Subsites (GroupID, SubsiteID) VALUES (?, ?)");
        $stmt->bind_param("ii", $groupId, $subsiteId);
        $stmt->execute();
        $stmt->close();
        $message = 'Group access updated.';
        $messageType = 'success';
    }
}

// Load groups - also uses the schema-configured table name
$groups = [];
$groupTable = getGroupTableName($conn);
$sql = 'SELECT ID, Title, Code, SubsiteID, AccessAllSubsites FROM ' . $groupTable . ' ORDER BY Title ASC';
$result = $conn->query($sql);
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $groups[] = $row;
    }
}

// Load subsites for the dropdown
$subsites = [];
$stmt = $conn->prepare("SELECT ID, Title FROM Subsite ORDER BY Title ASC");
$stmt->execute();
$sresult = $stmt->get_result();
while ($row = $sresult->fetch_assoc()) {
    $subsites[] = $row;
}
$stmt->close();

// Load group-subsite assignments
$assignments = [];
$result = $conn->query("SELECT gs.GroupID, gs.SubsiteID, s.Title as SubsiteTitle FROM Group_Subsites gs LEFT JOIN Subsite s ON gs.SubsiteID = s.ID");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $assignments[$row['GroupID']][] = $row;
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Group Subsite Access - CMS Admin</title>
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
        .alert { padding: 10px 14px; border-radius: 3px; margin-bottom: 16px; font-size: 13px; }
        .alert-success { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
        .alert-warning { background: #fff8e1; color: #f57f17; border: 1px solid #ffecb3; }
        .toolbar { margin-bottom: 16px; display: flex; gap: 8px; align-items: center; }
        .btn { display: inline-block; padding: 6px 14px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; cursor: pointer; text-decoration: none; color: #333; background: #fff; }
        .btn-action { background: #005a93; color: #fff; border-color: #005a93; }
        .btn-warning { background: #e65100; color: #fff; border-color: #e65100; }
        table { width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }
        th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
        th { background: #fafafa; font-weight: 600; color: #666; text-transform: uppercase; font-size: 11px; }
        .section { margin-bottom: 32px; }
        .section h3 { font-size: 16px; font-weight: 500; margin-bottom: 12px; color: #444; }
        .tag { display: inline-block; padding: 2px 8px; background: #e3f2fd; color: #1565c0; border-radius: 3px; font-size: 11px; margin-right: 4px; }
        .form-inline { display: flex; gap: 8px; align-items: center; padding: 12px; background: #fafafa; border: 1px solid #eee; border-radius: 3px; margin-bottom: 16px; }
        .form-inline select, .form-inline input { padding: 6px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; }
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
        <h2>Group Subsite Access</h2>

        <?php if ($message): ?>
            <div class="alert alert-<?php echo $messageType; ?>"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>

        <div class="section">
            <h3>Migrate Default Records</h3>
            <p style="font-size:13px;color:#666;margin-bottom:12px;">Run the migration to sync group subsite assignments from the group table into the join table.</p>
            <form method="POST" action="/admin/subsites/groups.php">
                <input type="hidden" name="action" value="migrate_groups">
                <button type="submit" class="btn btn-warning">Run Migration</button>
            </form>
        </div>

        <div class="section">
            <h3>Assign Group to Subsite</h3>
            <form method="POST" action="/admin/subsites/groups.php" class="form-inline">
                <input type="hidden" name="action" value="add_group_subsite">
                <label>Group:</label>
                <select name="group_id">
                    <?php foreach ($groups as $g): ?>
                        <option value="<?php echo (int)$g['ID']; ?>"><?php echo htmlspecialchars($g['Title']); ?></option>
                    <?php endforeach; ?>
                </select>
                <label>Subsite:</label>
                <select name="subsite_id">
                    <?php foreach ($subsites as $s): ?>
                        <option value="<?php echo (int)$s['ID']; ?>"><?php echo htmlspecialchars($s['Title']); ?></option>
                    <?php endforeach; ?>
                </select>
                <button type="submit" class="btn btn-action">Assign</button>
            </form>
        </div>

        <div class="section">
            <h3>Current Groups</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Code</th>
                        <th>Subsite ID</th>
                        <th>Access All</th>
                        <th>Assigned Subsites</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($groups as $g): ?>
                    <tr>
                        <td><?php echo (int)$g['ID']; ?></td>
                        <td><?php echo htmlspecialchars($g['Title']); ?></td>
                        <td><?php echo htmlspecialchars($g['Code']); ?></td>
                        <td><?php echo (int)$g['SubsiteID']; ?></td>
                        <td><?php echo $g['AccessAllSubsites'] ? 'Yes' : 'No'; ?></td>
                        <td>
                            <?php if (isset($assignments[$g['ID']])): ?>
                                <?php foreach ($assignments[$g['ID']] as $a): ?>
                                    <span class="tag"><?php echo htmlspecialchars($a['SubsiteTitle'] ?? 'Site #'.$a['SubsiteID']); ?></span>
                                <?php endforeach; ?>
                            <?php else: ?>
                                <span style="color:#999">None</span>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
