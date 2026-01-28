<?php
session_start();

// Check if user is logged in with global-read access
if (!isset($_SESSION['user_logged_in']) || $_SESSION['user_logged_in'] !== true) {
    header('Location: login.php?error=auth');
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

$search_type = isset($_GET['search']) ? $_GET['search'] : 'devices';
$results = [];
$search_performed = false;
$error_message = '';

// Handle POST search requests
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $search_performed = true;
    
    if ($search_type == 'packages') {
        $package_search = isset($_POST['package']) ? $_POST['package'] : '';
        
        if (!empty($package_search)) {
            $query = "SELECT packages.name, packages.version, packages.architecture, packages.manager, devices.hostname, devices.ip_address 
                      FROM packages, devices 
                      WHERE packages.device_id = devices.device_id 
                      AND packages.name LIKE '%" . $_POST['package'] . "%' 
                      GROUP BY packages.name, devices.hostname 
                      ORDER BY packages.name";
            
            $result = $conn->query($query);
            if ($result === false) {
                $error_message = "Database error: " . $conn->error;
            } else {
                while ($row = $result->fetch_assoc()) {
                    $results[] = $row;
                }
            }
        }
    } elseif ($search_type == 'devices') {
        $device_search = isset($_POST['device']) ? mysqli_real_escape_string($conn, $_POST['device']) : '';
        
        if (!empty($device_search)) {
            $query = "SELECT * FROM devices WHERE hostname LIKE '%$device_search%' OR ip_address LIKE '%$device_search%'";
            $result = $conn->query($query);
            if ($result) {
                while ($row = $result->fetch_assoc()) {
                    $results[] = $row;
                }
            }
        }
    } elseif ($search_type == 'alerts') {
        $alert_search = isset($_POST['alert']) ? mysqli_real_escape_string($conn, $_POST['alert']) : '';
        
        if (!empty($alert_search)) {
            $query = "SELECT a.*, d.hostname FROM alerts a 
                      JOIN devices d ON a.device_id = d.device_id 
                      WHERE a.message LIKE '%$alert_search%' OR a.alert_type LIKE '%$alert_search%'";
            $result = $conn->query($query);
            if ($result) {
                while ($row = $result->fetch_assoc()) {
                    $results[] = $row;
                }
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMonitor - Search</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>NetMonitor</h1>
        <p class="subtitle">Network Monitoring &amp; Management Platform v2.4.3</p>
    </div>
    
    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="devices.php">Devices</a>
        <a href="alerts.php">Alerts</a>
        <a href="search.php" class="active">Search</a>
        <a href="logout.php">Logout (<?php echo htmlspecialchars($_SESSION['username']); ?>)</a>
    </nav>

    <div class="content">
        <h2>Global Search</h2>
        
        <div class="search-tabs">
            <a href="search.php?search=devices" class="tab <?php echo $search_type == 'devices' ? 'active' : ''; ?>">Devices</a>
            <a href="search.php?search=packages" class="tab <?php echo $search_type == 'packages' ? 'active' : ''; ?>">Packages</a>
            <a href="search.php?search=alerts" class="tab <?php echo $search_type == 'alerts' ? 'active' : ''; ?>">Alerts</a>
        </div>
        
        <?php if ($search_type == 'devices'): ?>
        <form method="POST" action="search.php?search=devices" class="search-form">
            <label for="device">Search Devices:</label>
            <input type="text" id="device" name="device" placeholder="Enter hostname or IP address..." required>
            <button type="submit">Search</button>
        </form>
        
        <?php if ($search_performed && count($results) > 0): ?>
        <h3>Device Results</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>OS</th>
                </tr>
            </thead>
            <tbody>
            <?php foreach ($results as $device): ?>
                <tr>
                    <td><?php echo htmlspecialchars($device['hostname']); ?></td>
                    <td><?php echo htmlspecialchars($device['ip_address']); ?></td>
                    <td><?php echo htmlspecialchars($device['device_type']); ?></td>
                    <td><?php echo htmlspecialchars($device['status']); ?></td>
                    <td><?php echo htmlspecialchars($device['os']); ?></td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
        <?php elseif ($search_performed): ?>
        <p class="no-results">No devices found matching your search.</p>
        <?php endif; ?>
        
        <?php elseif ($search_type == 'packages'): ?>
        <form method="POST" action="search.php?search=packages" class="search-form">
            <label for="package">Search Installed Packages:</label>
            <input type="text" id="package" name="package" placeholder="Enter package name..." required>
            <button type="submit">Search</button>
        </form>
        
        <?php if (!empty($error_message)): ?>
        <p class="error"><?php echo htmlspecialchars($error_message); ?></p>
        <?php endif; ?>
        
        <?php if ($search_performed && count($results) > 0): ?>
        <h3>Package Results</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Package Name</th>
                    <th>Version</th>
                    <th>Architecture</th>
                    <th>Manager</th>
                    <th>Device</th>
                    <th>IP Address</th>
                </tr>
            </thead>
            <tbody>
            <?php foreach ($results as $pkg): ?>
                <tr>
                    <td><?php echo htmlspecialchars($pkg['name']); ?></td>
                    <td><?php echo htmlspecialchars($pkg['version']); ?></td>
                    <td><?php echo htmlspecialchars($pkg['architecture']); ?></td>
                    <td><?php echo htmlspecialchars($pkg['manager']); ?></td>
                    <td><?php echo htmlspecialchars($pkg['hostname']); ?></td>
                    <td><?php echo htmlspecialchars($pkg['ip_address']); ?></td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
        <?php elseif ($search_performed): ?>
        <p class="no-results">No packages found matching your search.</p>
        <?php endif; ?>
        
        <?php elseif ($search_type == 'alerts'): ?>
        <form method="POST" action="search.php?search=alerts" class="search-form">
            <label for="alert">Search Alerts:</label>
            <input type="text" id="alert" name="alert" placeholder="Enter alert type or message..." required>
            <button type="submit">Search</button>
        </form>
        
        <?php if ($search_performed && count($results) > 0): ?>
        <h3>Alert Results</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Device</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Message</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
            <?php foreach ($results as $alert): ?>
                <tr class="severity-<?php echo htmlspecialchars($alert['severity']); ?>">
                    <td><?php echo htmlspecialchars($alert['hostname']); ?></td>
                    <td><?php echo htmlspecialchars($alert['alert_type']); ?></td>
                    <td><?php echo htmlspecialchars($alert['severity']); ?></td>
                    <td><?php echo htmlspecialchars($alert['message']); ?></td>
                    <td><?php echo htmlspecialchars($alert['created_at']); ?></td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
        <?php elseif ($search_performed): ?>
        <p class="no-results">No alerts found matching your search.</p>
        <?php endif; ?>
        
        <?php endif; ?>
    </div>
</div>

<footer>
    <p>NetMonitor v2.4.3 | <a href="admin.php">Administration</a></p>
</footer>

<?php $conn->close(); ?>
</body>
</html>
