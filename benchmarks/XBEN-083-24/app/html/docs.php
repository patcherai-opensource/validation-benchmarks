<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DB-GPT API Documentation</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="header">
        <h1>DB-GPT</h1>
        <nav>
            <a href="/" class="nav-link">SQL Editor</a>
            <a href="/charts.php" class="nav-link">Charts</a>
            <a href="/datasources.php" class="nav-link">Datasources</a>
            <a href="/docs.php" class="nav-link active">API Docs</a>
        </nav>
    </header>

    <main class="main-content">
        <h2 class="page-title">API Documentation</h2>
        
        <div class="card">
            <h3>SQL Query Execution</h3>
            <p>Execute SQL queries against connected datasources.</p>
            <pre><code>POST /api/v1/editor/sql/run.php

Request Body:
{
    "db_name": "blogDB",
    "sql": "SELECT * FROM users LIMIT 10"
}

Response:
{
    "success": true,
    "data": [...],
    "row_count": 10
}</code></pre>
        </div>

        <div class="card">
            <h3>Chart Data Generation</h3>
            <p>Execute SQL queries and format results for chart visualization.</p>
            <pre><code>POST /api/v1/editor/chart/run.php

Request Body:
{
    "db_name": "blogDB",
    "sql": "SELECT category, COUNT(*) as count FROM items GROUP BY category",
    "chart_type": "bar"
}

Response:
{
    "success": true,
    "chart_type": "bar",
    "data": [...],
    "row_count": 5
}</code></pre>
        </div>

        <div class="card">
            <h3>Supported Databases</h3>
            <ul style="padding-left: 20px; margin-top: 10px;">
                <li>MySQL / MariaDB</li>
                <li>PostgreSQL</li>
                <li>SQLite</li>
                <li>DuckDB</li>
            </ul>
        </div>
    </main>

    <footer class="footer">
        <p>DB-GPT v0.7.0 | API Documentation</p>
    </footer>
</div>
</body>
</html>