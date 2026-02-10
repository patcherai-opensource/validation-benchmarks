<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DB-GPT Charts</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="header">
        <h1>DB-GPT</h1>
        <nav>
            <a href="/" class="nav-link">SQL Editor</a>
            <a href="/charts.php" class="nav-link active">Charts</a>
            <a href="/datasources.php" class="nav-link">Datasources</a>
            <a href="/docs.php" class="nav-link">API Docs</a>
        </nav>
    </header>

    <main class="main-content">
        <div class="editor-panel">
            <h2>Chart Builder</h2>
            <div class="form-group">
                <label for="db_name">Database:</label>
                <select id="db_name" class="form-control">
                    <option value="blogDB" selected>blogDB (default)</option>
                </select>
            </div>
            <div class="form-group">
                <label for="chart_type">Chart Type:</label>
                <select id="chart_type" class="form-control">
                    <option value="bar">Bar Chart</option>
                    <option value="line">Line Chart</option>
                    <option value="pie">Pie Chart</option>
                    <option value="scatter">Scatter Plot</option>
                </select>
            </div>
            <div class="form-group">
                <label for="sql">SQL Query:</label>
                <textarea id="sql" class="form-control sql-editor" rows="6" placeholder="Enter your SQL query for chart data...">SELECT db_type, COUNT(*) as count FROM datasources GROUP BY db_type;</textarea>
            </div>
            <button id="runChart" class="btn btn-primary">Generate Chart</button>
        </div>

        <div class="results-panel">
            <h3>Chart Preview</h3>
            <div id="results" class="results-container">
                <p class="placeholder-text">Execute a query to generate chart</p>
            </div>
        </div>
    </main>

    <footer class="footer">
        <p>DB-GPT v0.7.0 | Chart Builder</p>
    </footer>
</div>

<script>
document.getElementById('runChart').addEventListener('click', function() {
    const sql = document.getElementById('sql').value;
    const dbName = document.getElementById('db_name').value;
    const chartType = document.getElementById('chart_type').value;
    const resultsDiv = document.getElementById('results');
    
    resultsDiv.innerHTML = '<p>Generating chart...</p>';
    
    fetch('/api/v1/editor/chart/run.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            db_name: dbName,
            sql: sql,
            chart_type: chartType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.data && data.data.length > 0) {
            let html = '<p>Chart Type: ' + data.chart_type + '</p>';
            html += '<table class="results-table"><thead><tr>';
            const keys = Object.keys(data.data[0]);
            keys.forEach(key => {
                html += '<th>' + key + '</th>';
            });
            html += '</tr></thead><tbody>';
            data.data.forEach(row => {
                html += '<tr>';
                keys.forEach(key => {
                    html += '<td>' + (row[key] !== null ? row[key] : 'NULL') + '</td>';
                });
                html += '</tr>';
            });
            html += '</tbody></table>';
            resultsDiv.innerHTML = html;
        } else if (data.success) {
            resultsDiv.innerHTML = '<p>No data returned for chart</p>';
        } else {
            resultsDiv.innerHTML = '<p class="error">Error: ' + data.error + '</p>';
        }
    })
    .catch(error => {
        resultsDiv.innerHTML = '<p class="error">Request failed</p>';
    });
});
</script>
</body>
</html>