<?php
session_start();
$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'subsiteDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Schema configuration - simulating SilverStripe's DataObject schema system
$schemaConfig = [
    'Administrators' => 'group_administrators',
    'Editors' => 'group_editors', 
    'Viewers' => 'group_viewers'
];

$selectedGroup = '';
$groupMembers = [];
$error = '';

// Handle group selection - this is where the vulnerability exists
// Similar to SilverStripe's tableName() returning unsanitized value
if (isset($_GET['group_class'])) {
    $groupClass = $_GET['group_class'];
    
    // Simulating schema->tableName() - the returned table name is NOT sanitized
    // In SilverStripe, this came from the schema registry
    // Here we allow arbitrary input to be used as the table name (VULNERABLE)
    $groupTable = $groupClass;
    
    // This mirrors the vulnerable pattern from SilverStripe:
    // DB::query('SELECT ... FROM "' . $groupTable . '" ...')
    // The table name is inserted directly without escaping
    $query = 'SELECT id, member_name, email, access_level FROM ' . $groupTable . ' WHERE active = 1 ORDER BY member_name';
    
    $result = $conn->query($query);
    
    if ($result === false) {
        $error = "Query error: " . $conn->error;
    } else {
        while ($row = $result->fetch_assoc()) {
            $groupMembers[] = $row;
        }
    }
    $selectedGroup = $groupClass;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SilverSubsite CMS - Group Management</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="cms-header">
        <h1>SilverSubsite CMS</h1>
        <p class="tagline">Group Management</p>
    </header>

    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="groups.php" class="active">Group Management</a>
        <a href="subsites.php">Subsites</a>
        <a href="settings.php">Settings</a>
        <a href="admin.php">Admin Panel</a>
    </nav>

    <section class="group-management">
        <h2>User Groups</h2>
        <p>Select a group class to view members and permissions.</p>
        
        <form method="GET" action="groups.php" class="group-selector">
            <label for="group_class">Group Class:</label>
            <select name="group_class" id="group_class">
                <option value="">-- Select Group --</option>
                <?php foreach ($schemaConfig as $className => $tableName): ?>
                    <option value="<?php echo htmlspecialchars($tableName); ?>" <?php echo ($selectedGroup === $tableName) ? 'selected' : ''; ?>>
                        <?php echo htmlspecialchars($className); ?>
                    </option>
                <?php endforeach; ?>
            </select>
            <button type="submit" class="btn-primary">Load Group</button>
        </form>

        <?php if ($error): ?>
            <div class="error-box">
                <strong>Error:</strong> <?php echo htmlspecialchars($error); ?>
            </div>
        <?php endif; ?>

        <?php if (!empty($groupMembers)): ?>
            <h3>Members of: <?php echo htmlspecialchars($selectedGroup); ?></h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Access Level</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($groupMembers as $member): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($member['id']); ?></td>
                            <td><?php echo htmlspecialchars($member['member_name']); ?></td>
                            <td><?php echo htmlspecialchars($member['email']); ?></td>
                            <td><?php echo htmlspecialchars($member['access_level']); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php elseif ($selectedGroup && !$error): ?>
            <p>No members found in this group.</p>
        <?php endif; ?>
    </section>
    
    <section class="api-docs">
        <h3>Developer Note</h3>
        <p>The group management system uses the DataObject schema to resolve table names dynamically. 
        Group class names are mapped to their corresponding database tables.</p>
    </section>
</div>
<?php $conn->close(); ?>
</body>
</html>
