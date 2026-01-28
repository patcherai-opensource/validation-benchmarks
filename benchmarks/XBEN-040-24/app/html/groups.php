<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    // Get group class parameter for filtering - this determines which group table schema to use
    // Similar to SilverStripe's GroupSubsites extension pattern where table names are derived from class
    $groupClass = isset($_GET['group_class']) ? $_GET['group_class'] : 'user_groups';
    
    // Action handling
    $action = isset($_GET['action']) ? $_GET['action'] : 'list';
    $message = '';
    
    // Handle subsite assignment (POST)
    if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['assign_subsite'])) {
        $group_id = intval($_POST['group_id']);
        $subsite_id = intval($_POST['subsite_id']);
        
        // VULNERABLE: Table/class name from user input used in SQL without proper escaping
        // This mirrors the CVE pattern where tableName(Group::class) is used unsanitized
        $groupTable = $groupClass;
        
        // Check if group exists - injection point via backtick escape
        // Payload example: user_groups` WHERE 1=0 UNION SELECT password,2 FROM cms_administrators WHERE `id
        $checkQuery = "SELECT id, subsite_id FROM `" . $groupTable . "` WHERE id = " . $group_id;
        $result = $conn->query($checkQuery);
        
        if ($result === false) {
            $message = "Database error: " . $conn->error;
        } elseif ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $message = "Group #" . $row['id'] . " found with subsite_id: " . $row['subsite_id'];
        } else {
            $message = "Group not found in the specified class.";
        }
    }
    
    // Handle default records setup (migration-like operation)  
    // This is the primary injection point similar to requireDefaultRecords() in the CVE
    if (isset($_GET['action']) && $_GET['action'] == 'setup_defaults') {
        $groupTable = $groupClass;
        
        // VULNERABLE: Similar to requireDefaultRecords() in the CVE
        // Query with unsanitized table/class name - allows UNION-based extraction
        $selectQuery = "SELECT id, name, subsite_id FROM `" . $groupTable . "` WHERE subsite_id > 0";
        $result = $conn->query($selectQuery);
        
        if ($result === false) {
            $message = "Setup error: " . $conn->error;
        } else {
            $count = $result->num_rows;
            $message = "Found " . $count . " groups with subsite assignments.";
            
            // Display results for debugging/feedback
            if ($count > 0) {
                $message .= " Records: ";
                while ($row = $result->fetch_assoc()) {
                    $message .= "[" . $row['id'] . ":" . $row['name'] . "] ";
                }
            }
        }
    }
    
    // Lookup action - allows querying group details with class context
    if (isset($_GET['action']) && $_GET['action'] == 'lookup' && isset($_GET['id'])) {
        $groupTable = $groupClass;
        $lookup_id = intval($_GET['id']);
        
        // VULNERABLE: Union-based SQL injection via table name
        $lookupQuery = "SELECT id, name, description, subsite_id FROM `" . $groupTable . "` WHERE id = " . $lookup_id;
        $result = $conn->query($lookupQuery);
        
        if ($result === false) {
            $message = "Lookup error: " . $conn->error;
        } elseif ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $message = "Group Details - ID: " . $row['id'] . ", Name: " . $row['name'] . ", Description: " . $row['description'] . ", SubSite: " . $row['subsite_id'];
        } else {
            $message = "Group not found.";
        }
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Group Management - SubSite Manager</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Group Management</h1>
    <p class="subtitle">Manage user groups and subsite permissions</p>
    
    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="subsites.php">SubSites</a>
        <a href="groups.php" class="active">Groups</a>
        <a href="members.php">Members</a>
        <a href="settings.php">Settings</a>
        <a href="cms-admin.php">CMS Admin</a>
    </nav>

    <?php if ($message): ?>
    <div class="message-box"><?php echo htmlspecialchars($message); ?></div>
    <?php endif; ?>

    <div class="group-filter">
        <h3>Select Group Class</h3>
        <form method="GET" action="groups.php">
            <label for="group_class">Group Type:</label>
            <select name="group_class" id="group_class" onchange="this.form.submit()">
                <option value="user_groups" <?php echo $groupClass == 'user_groups' ? 'selected' : ''; ?>>Standard Groups</option>
                <option value="admin_groups" <?php echo $groupClass == 'admin_groups' ? 'selected' : ''; ?>>Admin Groups</option>
                <option value="content_groups" <?php echo $groupClass == 'content_groups' ? 'selected' : ''; ?>>Content Editor Groups</option>
            </select>
        </form>
    </div>

    <div class="group-list">
        <h2>Groups in: <?php echo htmlspecialchars($groupClass); ?></h2>
        <?php
        // Safe query for display - uses escaped value (intentionally different from vulnerable paths)
        $safeTable = mysqli_real_escape_string($conn, $groupClass);
        
        // Check if table exists
        $tableCheck = $conn->query("SHOW TABLES LIKE '$safeTable'");
        if ($tableCheck && $tableCheck->num_rows > 0) {
            $groupsQuery = "SELECT * FROM `$safeTable` ORDER BY name";
            $groups = $conn->query($groupsQuery);
            
            if ($groups && $groups->num_rows > 0) {
                echo "<table class='data-table'>";
                echo "<tr><th>ID</th><th>Name</th><th>Description</th><th>SubSite</th><th>Actions</th></tr>";
                while($row = $groups->fetch_assoc()) {
                    $subsite = $row['subsite_id'] > 0 ? "Site #" . $row['subsite_id'] : "All Sites";
                    echo "<tr>";
                    echo "<td>{$row['id']}</td>";
                    echo "<td>" . htmlspecialchars($row['name']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['description']) . "</td>";
                    echo "<td>{$subsite}</td>";
                    echo "<td><a href='groups.php?action=lookup&id={$row['id']}&group_class=" . urlencode($groupClass) . "'>View</a></td>";
                    echo "</tr>";
                }
                echo "</table>";
            } else {
                echo "<p>No groups found in this class.</p>";
            }
        } else {
            echo "<p>Group class not found. Please select a valid group type.</p>";
        }
        ?>
    </div>

    <div class="group-actions">
        <h3>Administrative Actions</h3>
        <ul>
            <li><a href="groups.php?action=setup_defaults&group_class=<?php echo urlencode($groupClass); ?>">Initialize Default Records</a></li>
            <li><a href="groups.php?action=sync&group_class=<?php echo urlencode($groupClass); ?>">Sync Group Permissions</a></li>
            <li><a href="groups.php?action=manage">Manage All Permissions</a></li>
        </ul>
    </div>

    <div class="subsite-assignment">
        <h3>Assign Group to SubSite</h3>
        <form method="POST" action="groups.php?group_class=<?php echo urlencode($groupClass); ?>">
            <input type="hidden" name="assign_subsite" value="1">
            <div class="form-group">
                <label for="group_id">Group ID:</label>
                <input type="number" name="group_id" id="group_id" required min="1" value="1">
            </div>
            <div class="form-group">
                <label for="subsite_id">SubSite ID:</label>
                <input type="number" name="subsite_id" id="subsite_id" required min="0" value="0">
            </div>
            <button type="submit" class="btn-primary">Check Assignment</button>
        </form>
    </div>
</div>

<footer>
    <p>&copy; 2024 SubSite Manager v3.2.1</p>
</footer>
<?php $conn->close(); ?>
</body>
</html>
