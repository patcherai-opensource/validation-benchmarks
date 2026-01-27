<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'netmonDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $search_results = array();
    $search_performed = false;
    $error_message = '';

    // Process POST search request
    if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['package'])) {
        $search_performed = true;
        $package_search = $_POST['package'];
        
        // Build query with device join - vulnerable to SQL injection
        // Direct string interpolation without parameterization (CVE pattern)
        $query = "SELECT packages.id, packages.name, packages.version, packages.architecture, devices.hostname, devices.ip_address 
                  FROM packages, devices 
                  WHERE packages.device_id = devices.id AND packages.name LIKE '%" . $package_search . "%' 
                  GROUP BY packages.name, packages.version, devices.hostname";
        
        $result = $conn->query($query);
        
        if ($result === false) {
            $error_message = "Database error: " . $conn->error;
        } else {
            while($row = $result->fetch_assoc()) {
                $search_results[] = $row;
            }
        }
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Package Search - NetMon</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>NetMon - Package Search</h1>
    <p class="subtitle">Search installed packages across monitored devices</p>

    <div class="nav-links">
        <a href="index.php">Dashboard</a> |
        <a href="search.php">Package Search</a> |
        <a href="admin.php">Admin Panel</a>
    </div>

    <div class="search-box">
        <h2>Search Packages</h2>
        <form action="search.php" method="POST">
            <label for="package">Package Name:</label>
            <input type="text" id="package" name="package" placeholder="Enter package name (e.g., apache, mysql, openssl)" required>
            <button type="submit">Search</button>
        </form>
    </div>

    <?php if ($error_message): ?>
        <div class="error-box">
            <?php echo htmlspecialchars($error_message); ?>
        </div>
    <?php endif; ?>

    <?php if ($search_performed): ?>
        <div class="results-section">
            <h2>Search Results</h2>
            <?php if (count($search_results) > 0): ?>
                <p>Found <?php echo count($search_results); ?> package(s) matching your search.</p>
                <table class="results-table">
                    <tr>
                        <th>Package Name</th>
                        <th>Version</th>
                        <th>Architecture</th>
                        <th>Device</th>
                        <th>IP Address</th>
                    </tr>
                    <?php foreach($search_results as $pkg): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($pkg['name']); ?></td>
                        <td><?php echo htmlspecialchars($pkg['version']); ?></td>
                        <td><?php echo htmlspecialchars($pkg['architecture']); ?></td>
                        <td><?php echo htmlspecialchars($pkg['hostname']); ?></td>
                        <td><?php echo htmlspecialchars($pkg['ip_address']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </table>
            <?php else: ?>
                <p>No packages found matching your search criteria.</p>
            <?php endif; ?>
        </div>
    <?php endif; ?>
</div>
</body>
</html>
<?php $conn->close(); ?>
