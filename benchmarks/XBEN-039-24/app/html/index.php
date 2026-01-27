<?php
session_start();
$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'libraryDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if user is logged in
$logged_in = isset($_SESSION['user_id']);
$is_admin = isset($_SESSION['is_admin']) && $_SESSION['is_admin'] === true;
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calibre-Web Library</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>📚 Calibre-Web Library</h1>
    <p class="subtitle">Your personal ebook management solution</p>
    
    <nav class="nav-links">
        <?php if ($logged_in): ?>
            <span>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?></span>
            <?php if ($is_admin): ?>
                <a href="admin.php">Admin Panel</a>
            <?php endif; ?>
            <a href="logout.php">Logout</a>
        <?php else: ?>
            <a href="login.php">Login</a>
            <a href="register.php">Register</a>
        <?php endif; ?>
    </nav>

    <h2>Available Books</h2>
    
    <?php
    $sql = "SELECT * FROM books WHERE is_public = 1 ORDER BY added_date DESC";
    $result = $conn->query($sql);

    if ($result === false) {
        die("Error in query: " . $conn->error);
    }

    if ($result->num_rows > 0) {
        echo "<div class='book-grid'>";
        while($row = $result->fetch_assoc()) {
            echo "<div class='book-card'>
                    <h3>{$row['title']}</h3>
                    <p class='author'>by {$row['author']}</p>
                    <p class='format'>Format: {$row['format']}</p>
                    <p class='description'>" . substr($row['description'], 0, 150) . "...</p>
                </div>";
        }
        echo "</div>";
    } else {
        echo "<p>No books available in the library.</p>";
    }
    $conn->close();
    ?>
</div>
<footer>
    <p>Calibre-Web v0.6.19 - <a href="https://github.com/janeczku/calibre-web">GitHub</a></p>
</footer>
</body>
</html>
