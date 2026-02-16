<?php
    $conn = new mysqli(getenv('MYSQL_HOST') ?: '127.0.0.1', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'cmsDB');
    if ($conn->connect_error) {
        die("Service Unavailable");
    }

    $result = $conn->query("SELECT id, `key`, title FROM documents WHERE `type` = 'page' AND published = 1 ORDER BY id ASC");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corporate Portal</title>
    <link rel="stylesheet" href="/assets/css/styles.css">
</head>
<body>
<div class="site-header">
    <div class="container">
        <h1>Corporate Portal</h1>
        <nav>
            <?php
            if ($result && $result->num_rows > 0) {
                while ($row = $result->fetch_assoc()) {
                    echo "<a href='/{$row['key']}'>" . htmlspecialchars($row['title']) . "</a> ";
                }
            }
            ?>
        </nav>
    </div>
</div>
<div class="container main-content">
    <h2>Welcome to Our Corporate Portal</h2>
    <p>This is the main landing page of our content management platform.</p>
    <div class="content-grid">
        <div class="card">
            <h3>About Us</h3>
            <p>Learn more about our company and mission.</p>
        </div>
        <div class="card">
            <h3>Services</h3>
            <p>Explore our range of consulting and development services.</p>
        </div>
        <div class="card">
            <h3>Contact</h3>
            <p>Get in touch with our team.</p>
        </div>
    </div>
</div>
<div class="site-footer">
    <div class="container">
        <p>&copy; 2024 Corporate Portal. All rights reserved.</p>
    </div>
</div>
<?php $conn->close(); ?>
</body>
</html>
