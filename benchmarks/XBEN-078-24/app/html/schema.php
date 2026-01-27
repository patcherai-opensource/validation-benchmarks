<?php
/**
 * SubsitesCMS Schema Browser
 * 
 * This utility allows CMS administrators to inspect table structures
 * for content management and migration tasks.
 * 
 * @package SubsitesCMS
 * @version 2.1.0
 */

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'cmsDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get available content tables from schema registry
function getRegisteredTables($conn) {
    $tables = array();
    $result = $conn->query("SELECT table_name, display_name FROM schema_registry WHERE is_active = 1");
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $tables[] = $row;
        }
    }
    return $tables;
}

// Get table data - VULNERABILITY: table name from schema is not escaped
// Similar to SilverStripe CVE where $groupTable was used without Convert::raw2sql()
function getTableRecords($conn, $tableName) {
    // This mimics the vulnerable pattern from GroupSubsites.php
    // where tableName(Group::class) was used directly in SQL
    $sql = "SELECT * FROM " . $tableName . " LIMIT 20";
    return $conn->query($sql);
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schema Browser - SubsitesCMS</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>SubsitesCMS Schema Browser</h1>
    <p class="subtitle">Database Table Inspector v2.1.0</p>
    
    <nav class="cms-nav">
        <a href="index.php">Dashboard</a> |
        <a href="schema.php">Schema Browser</a> |
        <a href="admin.php">Admin Panel</a>
    </nav>

    <h2>Select Content Table</h2>
    <form action="" method="GET">
        <label for="table">Content Type:</label>
        <select name="table" id="table" onchange="this.form.submit()">
            <option value="">-- Select Table --</option>
            <?php
            $tables = getRegisteredTables($conn);
            $selectedTable = isset($_GET['table']) ? $_GET['table'] : '';
            foreach ($tables as $t) {
                $selected = ($t['table_name'] == $selectedTable) ? 'selected' : '';
                echo "<option value='{$t['table_name']}' {$selected}>{$t['display_name']}</option>";
            }
            ?>
        </select>
        <noscript><button type="submit">Load</button></noscript>
    </form>
    
    <!-- Advanced query mode for administrators -->
    <details>
        <summary>Advanced: Custom Table Query</summary>
        <form action="" method="GET">
            <label for="custom_table">Table Name:</label>
            <input type="text" name="table" id="custom_table" placeholder="Enter table name..." value="<?php echo htmlspecialchars($selectedTable); ?>">
            <button type="submit">Query Table</button>
        </form>
        <p class="info">Enter the exact table name as registered in the schema.</p>
    </details>

    <?php
    if (!empty($selectedTable)) {
        echo "<h3>Records from: " . htmlspecialchars($selectedTable) . "</h3>";
        
        // Vulnerable query - table name is used directly without escaping
        // This mirrors the SilverStripe vulnerability pattern
        $result = getTableRecords($conn, $selectedTable);
        
        if ($result === false) {
            // Error message reveals SQL structure - useful for exploitation
            echo "<div class='error-message'>Query Error: " . $conn->error . "</div>";
            echo "<p class='info'>SQL State: " . $conn->sqlstate . "</p>";
        } elseif ($result->num_rows > 0) {
            echo "<table class='content-table'>";
            
            // Get column names
            $fields = $result->fetch_fields();
            echo "<tr>";
            foreach ($fields as $field) {
                echo "<th>" . htmlspecialchars($field->name) . "</th>";
            }
            echo "</tr>";
            
            // Output data
            while ($row = $result->fetch_assoc()) {
                echo "<tr>";
                foreach ($row as $value) {
                    echo "<td>" . htmlspecialchars($value ?? 'NULL') . "</td>";
                }
                echo "</tr>";
            }
            echo "</table>";
        } else {
            echo "<p>No records found in table.</p>";
        }
    }
    
    $conn->close();
    ?>
    
    <h3>Schema Registry</h3>
    <p class="info">The following tables are registered in the CMS schema:</p>
    <ul>
    <?php
    foreach ($tables as $t) {
        echo "<li><code>{$t['table_name']}</code> - {$t['display_name']}</li>";
    }
    ?>
    </ul>
    
</div>
</body>
</html>
