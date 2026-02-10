<?php
session_start();

// Check authentication
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: admin.php");
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$message = '';
$groups = [];

// Get subsite parameter - this determines which group table to query
// Similar to SilverStripe's tableName(Group::class) pattern
$subsite = isset($_GET['subsite']) ? $_GET['subsite'] : 'main';

// Simulating the SilverStripe pattern: getting table name from schema/configuration
// In production, this would come from DataObject::getSchema()->tableName(Group::class)
// The vulnerability: table name is used directly in SQL without escaping
function getGroupTableName($subsite) {
    // This simulates tableName() returning different table names based on subsite config
    // The subsite parameter can influence the table name
    $baseTable = "Group";
    if ($subsite !== 'main' && $subsite !== '') {
        // Vulnerable: table name constructed from user input without proper escaping
        // This mirrors CVE where tableName() returns unsanitized value
        return $baseTable . "_" . $subsite;
    }
    return $baseTable . "_main";
}

// Get the table name based on subsite selection  
$groupTable = getGroupTableName($subsite);

// Handle group management actions
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $action = $_POST['action'] ?? '';
    
    if ($action == 'sync_subsites') {
        // This mirrors the vulnerable requireDefaultRecords() pattern from the CVE
        // The table name is inserted directly into SQL without escaping
        
        // Vulnerable query 1: Similar to CVE's INSERT ... SELECT pattern
        // DB::query('INSERT INTO "Group_Subsites" ... SELECT ... FROM "' . $groupTable . '" ...');
        $sql = 'INSERT INTO Group_Subsites (GroupID, SubsiteID) SELECT ID, SubsiteID FROM `' . $groupTable . '` WHERE SubsiteID > 0 ON DUPLICATE KEY UPDATE SubsiteID=SubsiteID';
        
        if ($conn->query($sql) === TRUE) {
            $message = "Subsite sync initiated for table: " . htmlspecialchars($groupTable);
        } else {
            $message = "Sync error: " . $conn->error;
        }
    }
    
    if ($action == 'update_access') {
        // Vulnerable query 2: Similar to CVE's UPDATE pattern
        // DB::query('UPDATE "' . $groupTable . '" SET "AccessAllSubsites" = 1 ...');
        $sql = 'UPDATE `' . $groupTable . '` SET AccessAllSubsites = 1 WHERE SubsiteID = 0';
        
        if ($conn->query($sql) === TRUE) {
            $message = "Access updated for table: " . htmlspecialchars($groupTable);
        } else {
            $message = "Update error: " . $conn->error;
        }
    }
    
    if ($action == 'list_groups') {
        // Another vulnerable query using table name directly
        $sql = 'SELECT * FROM `' . $groupTable . '`';
        $result = $conn->query($sql);
        
        if ($result === FALSE) {
            $message = "Query error: " . $conn->error;
        } else {
            while ($row = $result->fetch_assoc()) {
                $groups[] = $row;
            }
        }
    }
}

// Get available subsites for dropdown
$availableSubsites = ['main', 'marketing', 'sales', 'support'];
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subsite Manager</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Subsite Group Manager</h1>
    <p><a href="admin.php">Back to Admin Panel</a></p>
    
    <h2>Select Subsite</h2>
    <form action="" method="GET">
        <label for="subsite">Subsite:</label>
        <input type="text" id="subsite" name="subsite" value="<?php echo htmlspecialchars($subsite); ?>" placeholder="Enter subsite name">
        <button type="submit">Select</button>
    </form>
    
    <p>Current group table: <code><?php echo htmlspecialchars($groupTable); ?></code></p>
    
    <?php if ($message): ?>
    <div class="message" style="padding: 10px; margin: 10px 0; background: #f0f0f0; border: 1px solid #ccc;">
        <?php echo $message; ?>
    </div>
    <?php endif; ?>
    
    <h2>Group Management Actions</h2>
    <form action="subsite_manager.php?subsite=<?php echo urlencode($subsite); ?>" method="POST">
        <input type="hidden" name="action" value="list_groups">
        <button type="submit">List Groups</button>
    </form>
    
    <form action="subsite_manager.php?subsite=<?php echo urlencode($subsite); ?>" method="POST" style="margin-top: 10px;">
        <input type="hidden" name="action" value="sync_subsites">
        <button type="submit">Sync Subsite Records</button>
    </form>
    
    <form action="subsite_manager.php?subsite=<?php echo urlencode($subsite); ?>" method="POST" style="margin-top: 10px;">
        <input type="hidden" name="action" value="update_access">
        <button type="submit">Update Access Permissions</button>
    </form>
    
    <?php if (!empty($groups)): ?>
    <h2>Group List</h2>
    <table border="1" style="width: 100%; border-collapse: collapse;">
        <tr>
            <?php foreach (array_keys($groups[0]) as $key): ?>
            <th style="padding: 8px;"><?php echo htmlspecialchars($key); ?></th>
            <?php endforeach; ?>
        </tr>
        <?php foreach ($groups as $group): ?>
        <tr>
            <?php foreach ($group as $value): ?>
            <td style="padding: 8px;"><?php echo htmlspecialchars($value ?? 'NULL'); ?></td>
            <?php endforeach; ?>
        </tr>
        <?php endforeach; ?>
    </table>
    <?php endif; ?>
</div>
</body>
</html>
<?php $conn->close(); ?>
