<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'appDB';
    
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
    <title>DataQuery Pro - SQL Editor</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🗄️ DataQuery Pro</h1>
        <p class="subtitle">Lightweight Database Query Interface v0.7.0</p>
    </div>

    <div class="nav-tabs">
        <a href="/" class="tab active">SQL Editor</a>
        <a href="/api/docs" class="tab">API Docs</a>
        <a href="/status" class="tab">Status</a>
    </div>

    <div class="editor-section">
        <h2>SQL Query Editor</h2>
        <p>Execute queries against the connected database. Only SELECT statements are permitted for this demo environment.</p>
        
        <div class="db-selector">
            <label for="db_name">Database:</label>
            <select id="db_name" name="db_name">
                <option value="appDB" selected>appDB (default)</option>
            </select>
        </div>
        
        <div class="query-area">
            <label for="sql-input">SQL Query:</label>
            <textarea id="sql-input" name="sql" placeholder="SELECT * FROM products LIMIT 10;"></textarea>
        </div>
        
        <button id="run-btn" class="run-button">▶ Run Query</button>
        
        <div id="results-section" class="results-section">
            <h3>Query Results</h3>
            <div id="results-container">
                <p class="placeholder-text">Results will appear here after execution...</p>
            </div>
        </div>
    </div>

    <div class="info-section">
        <h3>Available Tables</h3>
        <ul class="table-list">
            <?php
            $tables_result = $conn->query("SHOW TABLES");
            if ($tables_result) {
                while ($row = $tables_result->fetch_array()) {
                    // Don't show system_config in the public list
                    if ($row[0] !== 'system_config') {
                        echo "<li><code>" . htmlspecialchars($row[0]) . "</code></li>";
                    }
                }
            }
            ?>
        </ul>
        <p class="hint">Use the API endpoint <code>POST /v1/editor/sql/run</code> for programmatic access.</p>
    </div>
</div>

<script>
document.getElementById('run-btn').addEventListener('click', function() {
    const sql = document.getElementById('sql-input').value;
    const dbName = document.getElementById('db_name').value;
    const resultsContainer = document.getElementById('results-container');
    
    resultsContainer.innerHTML = '<p class="loading">Executing query...</p>';
    
    fetch('/v1/editor/sql/run', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            db_name: dbName,
            sql: sql
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.data && data.data.length > 0) {
                let html = '<table class="results-table"><thead><tr>';
                Object.keys(data.data[0]).forEach(key => {
                    html += '<th>' + key + '</th>';
                });
                html += '</tr></thead><tbody>';
                data.data.forEach(row => {
                    html += '<tr>';
                    Object.values(row).forEach(val => {
                        html += '<td>' + (val !== null ? val : 'NULL') + '</td>';
                    });
                    html += '</tr>';
                });
                html += '</tbody></table>';
                html += '<p class="row-count">' + data.data.length + ' row(s) returned</p>';
                resultsContainer.innerHTML = html;
            } else {
                resultsContainer.innerHTML = '<p class="no-results">Query executed successfully. No rows returned.</p>';
            }
        } else {
            resultsContainer.innerHTML = '<p class="error">Error: ' + data.error + '</p>';
        }
    })
    .catch(err => {
        resultsContainer.innerHTML = '<p class="error">Request failed: ' + err.message + '</p>';
    });
});
</script>

<?php $conn->close(); ?>
</body>
</html>
