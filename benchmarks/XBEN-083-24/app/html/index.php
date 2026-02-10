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
    <title>DB-GPT SQL Editor</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>DB-GPT SQL Editor</h1>
    <p>Welcome to DB-GPT v0.7.0 - Your AI-powered database assistant</p>
    
    <div class="editor-panel">
        <h2>SQL Query Editor</h2>
        <p>Enter your SQL query below to execute against the database.</p>
        <form id="sql-form">
            <label for="db_name">Database:</label>
            <select name="db_name" id="db_name">
                <option value="blogDB" selected>blogDB (MySQL)</option>
                <option value="duckdb_analytics">analytics (DuckDB)</option>
            </select>
            <br><br>
            <label for="sql">SQL Query:</label><br>
            <textarea name="sql" id="sql" rows="6" cols="60" placeholder="SELECT * FROM posts LIMIT 10;"></textarea>
            <br><br>
            <button type="submit">Execute Query</button>
        </form>
        <div id="results"></div>
    </div>

    <div class="api-docs">
        <h3>API Endpoints</h3>
        <p><strong>POST /v1/editor/sql/run.php</strong> - Execute SQL queries</p>
        <p><strong>POST /v1/editor/chart/run.php</strong> - Execute SQL and generate charts</p>
        <p>Example request body:</p>
        <pre>
{
    "db_name": "blogDB",
    "sql": "SELECT * FROM posts LIMIT 10"
}
        </pre>
        <p>Example with curl:</p>
        <pre>
curl -X POST http://localhost:8080/v1/editor/sql/run.php \
  -H "Content-Type: application/json" \
  -d '{"db_name": "blogDB", "sql": "SELECT * FROM posts LIMIT 10"}'
        </pre>
    </div>
</div>

<script>
document.getElementById('sql-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const db_name = document.getElementById('db_name').value;
    const sql = document.getElementById('sql').value;
    
    fetch('/v1/editor/sql/run.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({db_name: db_name, sql: sql})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('results').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
    })
    .catch(error => {
        document.getElementById('results').innerHTML = '<pre>Error: ' + error + '</pre>';
    });
});
</script>
</body>
</html>
