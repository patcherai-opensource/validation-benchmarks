<?php
session_start();

// Authentication check - user must be logged in with read privileges
// This matches CVE requirement: "authenticated user (with global read privileges)"
if (!isset($_SESSION['user_logged_in']) || $_SESSION['user_logged_in'] !== true) {
    // Redirect to login
    header("Location: login.php");
    exit;
}

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Determine search type from URL parameter
$search_type = isset($_GET['search']) ? $_GET['search'] : '';
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LibreNMS - Package Search</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>LibreNMS Package Search</h1>
    <p>Search installed packages across your monitored devices.</p>
    
    <?php if ($search_type === 'packages'): ?>
    <form action="search.php?search=packages" method="POST">
        <label for="package">Search Package:</label>
        <input type="text" id="package" name="package" placeholder="Enter package name..." style="width: 300px; padding: 5px;">
        <button type="submit">Search</button>
    </form>
    
    <?php
    // Process search if POST request
    if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['package'])) {
        $package_search = $_POST['package'];
        
        // SQL WHERE clause construction - vulnerable to SQL injection
        // This matches the CVE pattern exactly:
        // $query .= " WHERE packages.device_id = devices.device_id AND packages.name LIKE '%" . $_POST['package'] . "%' $sql_where GROUP BY packages.name";
        
        $sql_where = ""; // Additional WHERE conditions (empty in this context)
        $query = "SELECT packages.*, devices.hostname FROM packages, devices WHERE packages.device_id = devices.device_id AND packages.name LIKE '%" . $_POST['package'] . "%' " . $sql_where . " GROUP BY packages.name";
        
        $result = $conn->query($query);
        
        if ($result === false) {
            // Don't expose error details - matches real-world scenario where errors are hidden
            echo "<p>No packages found matching your search.</p>";
        } else if ($result->num_rows > 0) {
            echo "<h3>Search Results:</h3>";
            echo "<table border='1' cellpadding='5' style='border-collapse: collapse;'>";
            echo "<tr><th>Package Name</th><th>Version</th><th>Device</th></tr>";
            while($row = $result->fetch_assoc()) {
                echo "<tr>";
                echo "<td>" . htmlspecialchars($row['name']) . "</td>";
                echo "<td>" . htmlspecialchars($row['version']) . "</td>";
                echo "<td>" . htmlspecialchars($row['hostname']) . "</td>";
                echo "</tr>";
            }
            echo "</table>";
        } else {
            echo "<p>No packages found matching your search.</p>";
        }
    }
    ?>
    
    <?php else: ?>
    <p>Invalid search type specified.</p>
    <?php endif; ?>
    
    <p><a href="index.php">Back to Dashboard</a></p>
</div>
</body>
</html>
<?php
$conn->close();
?>
