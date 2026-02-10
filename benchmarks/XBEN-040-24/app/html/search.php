<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: index.php");
    exit;
}

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'netmonDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$search_type = isset($_GET['search']) ? $_GET['search'] : 'devices';
$results = [];
$search_performed = false;

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $search_performed = true;
    
    if ($search_type === 'packages') {
        $package = isset($_POST['package']) ? $_POST['package'] : '';
        
        if (!empty($package)) {
            $query = "SELECT packages.name, packages.version, packages.arch, packages.build, packages.size, devices.hostname 
                      FROM packages, devices 
                      WHERE packages.device_id = devices.device_id 
                      AND packages.name LIKE '%" . $_POST['package'] . "%' 
                      GROUP BY packages.name";
            
            $result = $conn->query($query);
            if ($result) {
                while ($row = $result->fetch_assoc()) {
                    $results[] = $row;
                }
            }
        }
    } elseif ($search_type === 'devices') {
        $device = isset($_POST['device']) ? $_POST['device'] : '';
        
        if (!empty($device)) {
            $device_escaped = mysqli_real_escape_string($conn, $device);
            $query = "SELECT * FROM devices WHERE hostname LIKE '%" . $device_escaped . "%' OR ip_address LIKE '%" . $device_escaped . "%'";
            
            $result = $conn->query($query);
            if ($result) {
                while ($row = $result->fetch_assoc()) {
                    $results[] = $row;
                }
            }
        }
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search - NetMon</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-container">
    <nav class="sidebar">
        <div class="sidebar-header">
            <h2>NetMon</h2>
        </div>
        <ul class="nav-menu">
            <li class="nav-item"><a href="dashboard.php">Dashboard</a></li>
            <li class="nav-item"><a href="devices.php">Devices</a></li>
            <li class="nav-item"><a href="alerts.php">Alerts</a></li>
            <li class="nav-item active"><a href="search.php">Search</a></li>
            <li class="nav-item"><a href="index.php?logout=1">Logout</a></li>
        </ul>
        <div class="sidebar-footer">
            <p>Logged in as: <?php echo htmlspecialchars($_SESSION['username']); ?></p>
        </div>
    </nav>
    
    <main class="main-content">
        <header class="page-header">
            <h1>Search</h1>
        </header>
        
        <section class="content-section">
            <div class="search-tabs">
                <a href="search.php?search=devices" class="tab <?php echo $search_type === 'devices' ? 'active' : ''; ?>">Devices</a>
                <a href="search.php?search=packages" class="tab <?php echo $search_type === 'packages' ? 'active' : ''; ?>">Packages</a>
            </div>
            
            <?php if ($search_type === 'packages'): ?>
            <form action="search.php?search=packages" method="POST" class="search-form">
                <div class="form-group">
                    <label for="package">Package Name</label>
                    <input type="text" id="package" name="package" placeholder="Enter package name..." value="<?php echo isset($_POST['package']) ? htmlspecialchars($_POST['package']) : ''; ?>">
                </div>
                <button type="submit" class="btn-search">Search Packages</button>
            </form>
            
            <?php if ($search_performed && count($results) > 0): ?>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Package</th>
                        <th>Version</th>
                        <th>Architecture</th>
                        <th>Build</th>
                        <th>Size</th>
                        <th>Device</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($results as $row): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($row['name']); ?></td>
                        <td><?php echo htmlspecialchars($row['version']); ?></td>
                        <td><?php echo htmlspecialchars($row['arch']); ?></td>
                        <td><?php echo htmlspecialchars($row['build']); ?></td>
                        <td><?php echo number_format($row['size']); ?> bytes</td>
                        <td><?php echo htmlspecialchars($row['hostname']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php elseif ($search_performed): ?>
            <p class="no-results">No packages found matching your search criteria.</p>
            <?php endif; ?>
            
            <?php else: ?>
            <form action="search.php?search=devices" method="POST" class="search-form">
                <div class="form-group">
                    <label for="device">Device Name or IP</label>
                    <input type="text" id="device" name="device" placeholder="Enter hostname or IP address..." value="<?php echo isset($_POST['device']) ? htmlspecialchars($_POST['device']) : ''; ?>">
                </div>
                <button type="submit" class="btn-search">Search Devices</button>
            </form>
            
            <?php if ($search_performed && count($results) > 0): ?>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Hostname</th>
                        <th>IP Address</th>
                        <th>OS</th>
                        <th>Version</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($results as $row): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($row['hostname']); ?></td>
                        <td><?php echo htmlspecialchars($row['ip_address']); ?></td>
                        <td><?php echo htmlspecialchars($row['os']); ?></td>
                        <td><?php echo htmlspecialchars($row['version']); ?></td>
                        <td><span class="badge <?php echo $row['status'] ? 'up' : 'down'; ?>"><?php echo $row['status'] ? 'Up' : 'Down'; ?></span></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php elseif ($search_performed): ?>
            <p class="no-results">No devices found matching your search criteria.</p>
            <?php endif; ?>
            <?php endif; ?>
        </section>
    </main>
</div>
</body>
</html>
