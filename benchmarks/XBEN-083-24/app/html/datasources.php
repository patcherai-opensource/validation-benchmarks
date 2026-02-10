<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        http_response_code(500);
        die("Service temporarily unavailable");
    }
    
    $datasources = [];
    $result = $conn->query("SELECT * FROM datasources ORDER BY name");
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $datasources[] = $row;
        }
    }
    $conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DB-GPT Datasources</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="header">
        <h1>DB-GPT</h1>
        <nav>
            <a href="/" class="nav-link">SQL Editor</a>
            <a href="/charts.php" class="nav-link">Charts</a>
            <a href="/datasources.php" class="nav-link active">Datasources</a>
            <a href="/docs.php" class="nav-link">API Docs</a>
        </nav>
    </header>

    <main class="main-content">
        <h2 class="page-title">Connected Datasources</h2>
        
        <div class="card">
            <h3>Registered Databases</h3>
            <?php if (count($datasources) > 0): ?>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Host</th>
                        <th>Port</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($datasources as $ds): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($ds['name']); ?></td>
                        <td><?php echo htmlspecialchars($ds['db_type']); ?></td>
                        <td><?php echo htmlspecialchars($ds['host']); ?></td>
                        <td><?php echo htmlspecialchars($ds['port']); ?></td>
                        <td><?php echo htmlspecialchars($ds['created_at']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php else: ?>
            <p class="placeholder-text">No datasources configured</p>
            <?php endif; ?>
        </div>
    </main>

    <footer class="footer">
        <p>DB-GPT v0.7.0 | Datasources</p>
    </footer>
</div>
</body>
</html>