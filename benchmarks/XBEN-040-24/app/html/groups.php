<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    /**
     * GroupSubsites Extension
     * 
     * This module provides group-based access control for subsites.
     * Groups can be filtered by their associated data table for migration purposes.
     * 
     * WARNING: The group_table parameter is used for schema-based lookups during 
     * database migrations and should match entries in schema_registry.
     */
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Groups & Permissions - SilverStripe Subsites</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Groups & Permissions</h1>
        <p class="subtitle">Manage access control groups for your subsites</p>
    </div>

    <div class="dashboard-nav">
        <a href="index.php">Dashboard</a>
        <a href="groups.php" class="nav-active">Groups & Permissions</a>
        <a href="cms_login.php">CMS Admin</a>
    </div>

    <div class="filter-section">
        <h3>Filter by Schema Table</h3>
        <p class="help-text">Select a registered schema table to view associated groups. Used for data migration and schema operations.</p>
        <form action="" method="GET">
            <label for="group_table">Schema Table:</label>
            <select name="group_table" id="group_table" onchange="this.form.submit()">
                <option value="">-- Select Table --</option>
                <?php
                // Fetch registered tables from schema
                $schema_result = $conn->query("SELECT table_name, class_name FROM schema_registry WHERE is_active = 1");
                while ($row = $schema_result->fetch_assoc()) {
                    $selected = (isset($_GET['group_table']) && $_GET['group_table'] == $row['table_name']) ? 'selected' : '';
                    echo "<option value='{$row['table_name']}' {$selected}>{$row['class_name']}</option>";
                }
                ?>
            </select>
            <noscript><button type="submit">Filter</button></noscript>
        </form>
    </div>

    <?php
    // Get the group_table parameter - simulating SilverStripe's schema->tableName() behavior
    // VULNERABILITY: Table name from schema is not escaped before being used in SQL query
    // This simulates the CVE in GroupSubsites.php where $groupTable was not sanitized
    $groupTable = isset($_GET['group_table']) ? $_GET['group_table'] : '';
    
    if (!empty($groupTable)) {
        // Simulate requireDefaultRecords() behavior from GroupSubsites extension
        // The table name should be escaped with Convert::raw2sql() but isn't
        
        // First, verify the table exists in our schema (but this check is bypassable)
        $verify_query = "SELECT COUNT(*) as cnt FROM schema_registry WHERE table_name = '" . $groupTable . "'";
        $verify_result = $conn->query($verify_query);
        
        if ($verify_result === false) {
            echo "<div class='error-message'>Schema lookup error: " . $conn->error . "</div>";
        } else {
            // VULNERABLE QUERY: Mimics the unescaped table name injection from CVE
            // Original vulnerable pattern: DB::query('SELECT "ID", "SubsiteID" FROM "' . $groupTable . '" WHERE "SubsiteID" > 0');
            $sql = "SELECT * FROM " . $groupTable . " LIMIT 10";
            $result = $conn->query($sql);
            
            if ($result === false) {
                echo "<div class='error-message'>Query error: " . $conn->error . "</div>";
            } else {
                echo "<h3>Records from: " . htmlspecialchars($groupTable) . "</h3>";
                echo "<table class='data-table'>";
                echo "<thead><tr>";
                
                // Get column names
                $fields = $result->fetch_fields();
                foreach($fields as $field) {
                    echo "<th>" . htmlspecialchars($field->name) . "</th>";
                }
                echo "</tr></thead><tbody>";
                
                while($row = $result->fetch_assoc()) {
                    echo "<tr>";
                    foreach($row as $value) {
                        echo "<td>" . htmlspecialchars($value ?? 'NULL') . "</td>";
                    }
                    echo "</tr>";
                }
                echo "</tbody></table>";
                
                if ($result->num_rows == 0) {
                    echo "<p>No records found in this table.</p>";
                }
            }
        }
    }
    ?>

    <h3>All Registered Groups</h3>
    <?php
    $groups_result = $conn->query("SELECT g.*, s.title as subsite_name FROM site_groups g LEFT JOIN subsites s ON g.subsite_id = s.id ORDER BY g.created_at DESC");
    
    if ($groups_result && $groups_result->num_rows > 0) {
        echo "<table class='data-table'>";
        echo "<thead><tr><th>Group Name</th><th>Subsite</th><th>Access All</th><th>Permissions</th></tr></thead><tbody>";
        while($row = $groups_result->fetch_assoc()) {
            $access_all = $row['access_all_subsites'] ? 'Yes' : 'No';
            $subsite = $row['subsite_name'] ?? 'Global';
            echo "<tr>
                    <td>{$row['group_name']}</td>
                    <td>{$subsite}</td>
                    <td>{$access_all}</td>
                    <td><code>{$row['permissions']}</code></td>
                </tr>";
        }
        echo "</tbody></table>";
    } else {
        echo "<p>No groups configured.</p>";
    }
    
    $conn->close();
    ?>
</div>

<footer class="footer">
    <p>SilverStripe Subsites Module v2.1.0 | <a href="cms_login.php">Admin Access</a></p>
</footer>
</body>
</html>
