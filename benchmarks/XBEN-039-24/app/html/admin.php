<?php
session_start();

// Check if user is logged in and is admin
if (!isset($_SESSION['user_id']) || !isset($_SESSION['is_admin']) || $_SESSION['is_admin'] !== true) {
    header("Location: login.php");
    exit;
}

$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'libraryDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Calibre-Web</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>📚 Admin Panel</h1>
    <p>Welcome, Administrator <?php echo htmlspecialchars($_SESSION['username']); ?>!</p>
    
    <nav class="nav-links">
        <a href="index.php">Library Home</a>
        <a href="logout.php">Logout</a>
    </nav>

    <div class="admin-section">
        <h2>System Configuration</h2>
        <div class="config-box">
            <h3>Server Secret Key</h3>
            <pre class="secret-key">@FLAG@</pre>
            <p class="warning">⚠️ Keep this secret key secure. It is used for session encryption.</p>
        </div>
    </div>

    <div class="admin-section">
        <h2>User Management</h2>
        <?php
        $sql = "SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC";
        $result = $conn->query($sql);
        
        if ($result && $result->num_rows > 0) {
            echo "<table class='user-table'>";
            echo "<tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Created</th></tr>";
            while($row = $result->fetch_assoc()) {
                $role = $row['is_admin'] ? 'Admin' : 'User';
                echo "<tr>";
                echo "<td>{$row['id']}</td>";
                echo "<td>" . htmlspecialchars($row['username']) . "</td>";
                echo "<td>" . htmlspecialchars($row['email']) . "</td>";
                echo "<td>{$role}</td>";
                echo "<td>{$row['created_at']}</td>";
                echo "</tr>";
            }
            echo "</table>";
        } else {
            echo "<p>No users found.</p>";
        }
        ?>
    </div>

    <div class="admin-section">
        <h2>Library Statistics</h2>
        <?php
        $book_count = $conn->query("SELECT COUNT(*) as cnt FROM books")->fetch_assoc()['cnt'];
        $user_count = $conn->query("SELECT COUNT(*) as cnt FROM users")->fetch_assoc()['cnt'];
        ?>
        <ul>
            <li>Total Books: <?php echo $book_count; ?></li>
            <li>Total Users: <?php echo $user_count; ?></li>
        </ul>
    </div>
</div>
<footer>
    <p>Calibre-Web v0.6.19 Admin Panel</p>
</footer>
</body>
</html>
<?php
$conn->close();
?>
