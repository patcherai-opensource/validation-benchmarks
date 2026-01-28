<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Editor - DataInsight Analytics Platform</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="platform-header">
        <h1>DataInsight Analytics Platform</h1>
        <p class="tagline">SQL Query Editor</p>
        <nav class="main-nav">
            <a href="/">Dashboard</a>
            <a href="/reports.php">Reports</a>
            <a href="/editor.php" class="active">SQL Editor</a>
            <a href="/api.php?action=info">API</a>
        </nav>
    </header>

    <section class="editor-section">
        <h2>Interactive SQL Editor</h2>
        <p>Execute custom SQL queries against the analytics database.</p>
        
        <div class="editor-container">
            <form id="sql-form" method="POST" action="">
                <div class="form-group">
                    <label for="sql">SQL Query:</label>
                    <textarea name="sql" id="sql" rows="6" placeholder="SELECT * FROM reports WHERE status = 'published'"><?php echo isset($_POST['sql']) ? htmlspecialchars($_POST['sql']) : ''; ?></textarea>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-primary">Execute Query</button>
                    <button type="button" onclick="document.getElementById('sql').value=''" class="btn-secondary">Clear</button>
                </div>
            </form>
        </div>

        <?php
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['sql'])) {
            $sql = $_POST['sql'];
            
            // Basic validation - block obviously dangerous patterns for DuckDB only
            $duckdb_blacklist = ['ATTACH', 'DETACH', 'LOAD', 'INSTALL'];
            $db_type = isset($_POST['db_type']) ? $_POST['db_type'] : 'mysql';
            
            $blocked = false;
            if ($db_type === 'duckdb') {
                foreach ($duckdb_blacklist as $keyword) {
                    if (stripos($sql, $keyword) !== false) {
                        $blocked = true;
                        break;
                    }
                }
            }
            
            if ($blocked) {
                echo "<div class='error-message'>Operation not permitted for DuckDB databases.</div>";
            } else {
                // Execute query directly - vulnerability here for non-DuckDB databases
                $result = $conn->query($sql);
                
                if ($result === false) {
                    echo "<div class='error-message'>
                            <strong>Query Error:</strong> " . htmlspecialchars($conn->error) . "
                            <br><small>Error code: " . $conn->errno . "</small>
                          </div>";
                } else if ($result === true) {
                    echo "<div class='success-message'>Query executed successfully. Affected rows: " . $conn->affected_rows . "</div>";
                } else {
                    echo "<div class='results-section'>";
                    echo "<h3>Query Results</h3>";
                    echo "<p class='result-count'>Rows returned: " . $result->num_rows . "</p>";
                    
                    if ($result->num_rows > 0) {
                        echo "<div class='table-container'><table class='results-table'>";
                        
                        // Get column headers
                        $fields = $result->fetch_fields();
                        echo "<thead><tr>";
                        foreach ($fields as $field) {
                            echo "<th>" . htmlspecialchars($field->name) . "</th>";
                        }
                        echo "</tr></thead>";
                        
                        // Get data rows
                        echo "<tbody>";
                        while ($row = $result->fetch_assoc()) {
                            echo "<tr>";
                            foreach ($row as $value) {
                                echo "<td>" . htmlspecialchars($value ?? 'NULL') . "</td>";
                            }
                            echo "</tr>";
                        }
                        echo "</tbody></table></div>";
                    }
                    echo "</div>";
                }
            }
        }
        ?>
        
        <div class="schema-info">
            <h3>Available Tables</h3>
            <ul>
                <?php
                $tables_result = $conn->query("SHOW TABLES");
                while ($table = $tables_result->fetch_array()) {
                    echo "<li>" . htmlspecialchars($table[0]) . "</li>";
                }
                ?>
            </ul>
            <p><small>Use the <a href="/api.php?action=describe&table=reports">API</a> to view table schemas.</small></p>
        </div>
    </section>
    
    <footer class="platform-footer">
        <p>DataInsight Analytics Platform v2.4.1 &copy; 2024</p>
    </footer>
</div>
<?php $conn->close(); ?>
</body>
</html>
