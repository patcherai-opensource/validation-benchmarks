<?php
    $mysql_host = getenv('MYSQL_HOST') ?: '127.0.0.1';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'cmsDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        http_response_code(503);
        die('Service temporarily unavailable.');
    }

    $result = $conn->query("SELECT id, `key`, path, type FROM documents WHERE published = 1 AND type = 'page' ORDER BY path, `key`");
    $pages = [];
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $pages[] = $row;
        }
    }
    $conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Management System</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <h1>Content Management System</h1>
            <a href="/admin.php">Administration</a>
        </div>
    </header>
    <div class="container" style="padding-top: 30px;">
        <h2 style="margin-bottom: 15px;">Published Pages</h2>
        <?php if (count($pages) > 0): ?>
        <ul class="page-list">
            <?php foreach ($pages as $page): ?>
            <li>
                <strong><?php echo htmlspecialchars($page['key']); ?></strong>
                <span style="color:#888; margin-left: 10px;"><?php echo htmlspecialchars($page['path'] . $page['key']); ?></span>
            </li>
            <?php endforeach; ?>
        </ul>
        <?php else: ?>
        <p>No published pages available.</p>
        <?php endif; ?>
    </div>
</body>
</html>
