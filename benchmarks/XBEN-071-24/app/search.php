<?php
session_start();

// Check if user is logged in (authentication required as per CVE)
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: login.php");
    exit();
}

// Database connection
$servername = $_ENV['DB_HOST'] ?? "localhost";
$username = $_ENV['DB_USER'] ?? "challenge";
$password = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$type = $_GET['type'] ?? 'mac';
$results = [];
$searchPerformed = false;
$error = '';

// Handle search form submission
if ($_SERVER["REQUEST_METHOD"] == "POST" || isset($_GET['address'])) {
    $searchPerformed = true;
    
    // Get the address from POST or GET (AJAX support like LibreNMS)
    $address = $_POST['address'] ?? $_GET['address'] ?? '';
    
    if ($type === 'mac') {
        // VULNERABLE CODE - Direct string interpolation matching CVE-2023-5591
        // This is the exact vulnerable pattern from LibreNMS:
        // $sql .= " WHERE I.device_id = D.device_id AND `ifPhysAddress` LIKE '%" . trim(str_replace([':', ' ', '-', '.', '0x'], '', $vars['address'])) . "%' $where ";
        
        // Strip common MAC address separators (same as LibreNMS)
        $cleanedAddress = trim(str_replace([':', ' ', '-', '.', '0x'], '', $address));
        
        // VULNERABLE: Direct interpolation into SQL query
        $sql = "SELECT p.port_id, p.ifDescr, p.ifName, p.ifPhysAddress, p.ifOperStatus, p.ifSpeed, 
                       d.device_id, d.hostname, d.sysName, d.ip
                FROM ports p, devices d 
                WHERE p.device_id = d.device_id AND `ifPhysAddress` LIKE '%" . $cleanedAddress . "%'";
        
        $result = $conn->query($sql);
        
        if ($result === false) {
            $error = "Query error: " . $conn->error;
        } else {
            while ($row = $result->fetch_assoc()) {
                $results[] = $row;
            }
        }
    } else {
        // Other search types use prepared statements (safe)
        $stmt = $conn->prepare("SELECT d.device_id, d.hostname, d.sysName, d.ip, d.status FROM devices d WHERE d.ip LIKE ?");
        $searchParam = '%' . $address . '%';
        $stmt->bind_param("s", $searchParam);
        $stmt->execute();
        $result = $stmt->get_result();
        while ($row = $result->fetch_assoc()) {
            $results[] = $row;
        }
        $stmt->close();
    }
}

$conn->close();

// For AJAX table requests, return JSON
if (isset($_GET['format']) && $_GET['format'] === 'json') {
    header('Content-Type: application/json');
    echo json_encode(['data' => $results, 'error' => $error]);
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LibreNMS - <?php echo ucfirst($type); ?> Search</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }
        .navbar {
            background: #16213e;
            color: #fff;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar h1 { font-size: 22px; }
        .navbar h1 span { color: #e94560; }
        .navbar .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .navbar a {
            color: #fff;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 4px;
            transition: background 0.3s;
        }
        .navbar a:hover { background: rgba(255,255,255,0.1); }
        .navbar .logout { background: #e94560; }
        .navbar .logout:hover { background: #d63450; }
        
        .sidebar {
            position: fixed;
            left: 0;
            top: 60px;
            width: 220px;
            height: calc(100vh - 60px);
            background: #1a1a2e;
            padding: 20px 0;
        }
        .sidebar a {
            display: block;
            color: #aaa;
            text-decoration: none;
            padding: 12px 25px;
            transition: all 0.3s;
            border-left: 3px solid transparent;
        }
        .sidebar a:hover, .sidebar a.active {
            color: #fff;
            background: rgba(255,255,255,0.05);
            border-left-color: #e94560;
        }
        .sidebar .section-title {
            color: #666;
            font-size: 11px;
            text-transform: uppercase;
            padding: 20px 25px 10px;
            letter-spacing: 1px;
        }
        
        .main-content {
            margin-left: 220px;
            padding: 30px;
            margin-top: 60px;
        }
        .card {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 25px;
            margin-bottom: 20px;
        }
        .card h2 {
            color: #16213e;
            margin-bottom: 20px;
            font-size: 18px;
            border-bottom: 2px solid #e94560;
            padding-bottom: 10px;
        }
        .search-form {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        .search-form input[type="text"] {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e1e1e1;
            border-radius: 6px;
            font-size: 14px;
        }
        .search-form input[type="text"]:focus {
            outline: none;
            border-color: #e94560;
        }
        .search-form button {
            padding: 12px 25px;
            background: #e94560;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        .search-form button:hover {
            background: #d63450;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e1e1e1;
        }
        th {
            background: #16213e;
            color: #fff;
            font-weight: 500;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .status-up { color: #28a745; }
        .status-down { color: #dc3545; }
        .error {
            background: #fee;
            color: #c00;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .info-box {
            background: #e8f4fd;
            color: #0066cc;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .no-results {
            color: #666;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>Libre<span>NMS</span></h1>
        <div class="user-info">
            <span>Welcome, <?php echo htmlspecialchars($_SESSION['realname'] ?? $_SESSION['username']); ?></span>
            <a href="logout.php" class="logout">Logout</a>
        </div>
    </nav>
    
    <div class="sidebar">
        <div class="section-title">Overview</div>
        <a href="index.php">Dashboard</a>
        <a href="devices.php">Devices</a>
        
        <div class="section-title">Search</div>
        <a href="search.php?type=ipv4" <?php echo $type === 'ipv4' ? 'class="active"' : ''; ?>>IPv4 Address</a>
        <a href="search.php?type=ipv6" <?php echo $type === 'ipv6' ? 'class="active"' : ''; ?>>IPv6 Address</a>
        <a href="search.php?type=mac" <?php echo $type === 'mac' ? 'class="active"' : ''; ?>>MAC Address</a>
        <a href="search.php?type=arp" <?php echo $type === 'arp' ? 'class="active"' : ''; ?>>ARP Table</a>
        
        <div class="section-title">Reports</div>
        <a href="#">Alerts</a>
        <a href="#">Eventlog</a>
    </div>
    
    <main class="main-content">
        <div class="card">
            <h2><?php echo ucfirst($type); ?> Address Search</h2>
            
            <?php if ($type === 'mac'): ?>
            <div class="info-box">
                Search for interfaces by MAC address. Common separators (: - . space) are automatically removed.
                <br>Example: <code>00:1A:2B:3C:4D:5E</code> or <code>001A2B3C4D5E</code>
            </div>
            <?php endif; ?>
            
            <form method="POST" class="search-form">
                <input type="text" name="address" placeholder="Enter <?php echo $type === 'mac' ? 'MAC' : 'IP'; ?> address to search..." 
                       value="<?php echo htmlspecialchars($_POST['address'] ?? $_GET['address'] ?? ''); ?>">
                <button type="submit">Search</button>
            </form>
            
            <?php if ($error): ?>
                <div class="error"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            
            <?php if ($searchPerformed): ?>
                <?php if (count($results) > 0): ?>
                    <table>
                        <thead>
                            <tr>
                                <?php if ($type === 'mac'): ?>
                                <th>Device</th>
                                <th>Interface</th>
                                <th>MAC Address</th>
                                <th>Status</th>
                                <th>Speed</th>
                                <?php else: ?>
                                <th>Hostname</th>
                                <th>sysName</th>
                                <th>IP Address</th>
                                <th>Status</th>
                                <?php endif; ?>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($results as $row): ?>
                            <tr>
                                <?php if ($type === 'mac'): ?>
                                <td><?php echo htmlspecialchars($row['hostname'] ?? ''); ?></td>
                                <td><?php echo htmlspecialchars($row['ifName'] ?? $row['ifDescr'] ?? ''); ?></td>
                                <td><code><?php echo htmlspecialchars($row['ifPhysAddress'] ?? ''); ?></code></td>
                                <td class="<?php echo ($row['ifOperStatus'] ?? '') === 'up' ? 'status-up' : 'status-down'; ?>">
                                    <?php echo htmlspecialchars($row['ifOperStatus'] ?? ''); ?>
                                </td>
                                <td><?php echo $row['ifSpeed'] ? number_format($row['ifSpeed'] / 1000000) . ' Mbps' : ''; ?></td>
                                <?php else: ?>
                                <td><?php echo htmlspecialchars($row['hostname'] ?? ''); ?></td>
                                <td><?php echo htmlspecialchars($row['sysName'] ?? ''); ?></td>
                                <td><?php echo htmlspecialchars($row['ip'] ?? ''); ?></td>
                                <td class="<?php echo ($row['status'] ?? 0) == 1 ? 'status-up' : 'status-down'; ?>">
                                    <?php echo ($row['status'] ?? 0) == 1 ? 'up' : 'down'; ?>
                                </td>
                                <?php endif; ?>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                <?php else: ?>
                    <div class="no-results">No results found for your search.</div>
                <?php endif; ?>
            <?php endif; ?>
        </div>
    </main>
</body>
</html>
