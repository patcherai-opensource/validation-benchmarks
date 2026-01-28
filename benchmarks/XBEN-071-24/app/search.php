<?php
session_start();

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

$results = [];
$error = '';
$search_term = '';

if (isset($_GET['address']) && !empty($_GET['address'])) {
    $search_term = $_GET['address'];
    
    // Normalize MAC address - remove common separators (like LibreNMS does)
    // VULNERABLE: Direct interpolation into SQL query without proper parameterization
    $normalized = trim(str_replace([':', ' ', '-', '.', '0x'], '', $search_term));
    
    // Build the query - VULNERABLE SQL INJECTION
    // The normalized MAC address is directly concatenated into the LIKE clause
    $sql = "SELECT I.interface_id, I.ifName, I.ifPhysAddress, I.ifOperStatus, I.ifDescr, 
                   D.hostname, D.ip_address, D.device_type, D.location 
            FROM interfaces I, devices D 
            WHERE I.device_id = D.device_id AND `ifPhysAddress` LIKE '%" . $normalized . "%'";
    
    $result = $conn->query($sql);
    
    if ($result === false) {
        $error = "Database error: " . $conn->error;
    } else {
        while ($row = $result->fetch_assoc()) {
            $results[] = $row;
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
    <title>MAC Address Search - NetWatch Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f1a;
            color: #fff;
            min-height: 100vh;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .navbar h1 { color: #00d4ff; font-size: 22px; }
        .nav-links { display: flex; gap: 20px; align-items: center; }
        .nav-links a { color: #aaa; text-decoration: none; padding: 8px 16px; border-radius: 6px; transition: all 0.3s; }
        .nav-links a:hover, .nav-links a.active { background: rgba(0,212,255,0.1); color: #00d4ff; }
        .user-info { display: flex; align-items: center; gap: 15px; }
        .user-info span { color: #888; }
        .logout-btn { 
            background: rgba(255,0,0,0.1); 
            color: #ff6b6b; 
            padding: 8px 16px; 
            border-radius: 6px; 
            text-decoration: none;
        }
        .container { padding: 30px; max-width: 1400px; margin: 0 auto; }
        .page-header { margin-bottom: 30px; }
        .page-header h2 { font-size: 24px; margin-bottom: 10px; }
        .page-header p { color: #888; }
        .search-box {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }
        .search-form { display: flex; gap: 15px; align-items: flex-end; }
        .form-group { flex: 1; }
        .form-group label { display: block; color: #aaa; font-size: 14px; margin-bottom: 8px; }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 16px;
        }
        .form-group input:focus { outline: none; border-color: #00d4ff; }
        .search-btn {
            padding: 12px 30px;
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 16px;
            cursor: pointer;
        }
        .search-btn:hover { opacity: 0.9; }
        .results-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            overflow: hidden;
        }
        .results-table th, .results-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .results-table th { 
            background: rgba(0,0,0,0.3); 
            color: #00d4ff;
            font-weight: 600;
        }
        .results-table tr:hover { background: rgba(0,212,255,0.05); }
        .status-up { color: #00ff88; }
        .status-down { color: #ff6b6b; }
        .error-msg {
            background: rgba(255,0,0,0.1);
            border: 1px solid rgba(255,0,0,0.3);
            color: #ff6b6b;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .no-results {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        .help-text {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0,212,255,0.05);
            border-radius: 8px;
            font-size: 13px;
            color: #aaa;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>🌐 NetWatch Pro</h1>
        <div class="nav-links">
            <a href="dashboard.php">Dashboard</a>
            <a href="devices.php">Devices</a>
            <a href="search.php" class="active">MAC Search</a>
            <a href="alerts.php">Alerts</a>
            <a href="settings.php">Settings</a>
        </div>
        <div class="user-info">
            <span>Welcome, <?= htmlspecialchars($_SESSION['username']) ?></span>
            <a href="logout.php" class="logout-btn">Logout</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h2>🔍 MAC Address Search</h2>
            <p>Search network interfaces by their physical (MAC) address</p>
        </div>
        
        <div class="search-box">
            <form method="GET" action="search.php" class="search-form">
                <div class="form-group">
                    <label for="address">MAC Address</label>
                    <input type="text" id="address" name="address" 
                           placeholder="Enter MAC address (e.g., 00:1A:2B:3C:4D:EE or 001A2B3C4DEE)"
                           value="<?= htmlspecialchars($search_term) ?>">
                </div>
                <button type="submit" class="search-btn">Search</button>
            </form>
            <div class="help-text">
                <strong>Tip:</strong> You can enter MAC addresses in any format. Colons, dashes, dots, and spaces will be automatically removed for matching.
            </div>
        </div>
        
        <?php if ($error): ?>
        <div class="error-msg"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>
        
        <?php if (!empty($search_term)): ?>
            <?php if (count($results) > 0): ?>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Hostname</th>
                        <th>Interface</th>
                        <th>MAC Address</th>
                        <th>Status</th>
                        <th>IP Address</th>
                        <th>Location</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($results as $row): ?>
                    <tr>
                        <td><?= htmlspecialchars($row['hostname']) ?></td>
                        <td><?= htmlspecialchars($row['ifName']) ?></td>
                        <td><code><?= htmlspecialchars($row['ifPhysAddress']) ?></code></td>
                        <td class="<?= $row['ifOperStatus'] === 'up' ? 'status-up' : 'status-down' ?>">
                            <?= htmlspecialchars($row['ifOperStatus']) ?>
                        </td>
                        <td><?= htmlspecialchars($row['ip_address']) ?></td>
                        <td><?= htmlspecialchars($row['location']) ?></td>
                        <td><?= htmlspecialchars($row['ifDescr']) ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php else: ?>
            <div class="no-results">
                <p>No interfaces found matching "<strong><?= htmlspecialchars($search_term) ?></strong>"</p>
            </div>
            <?php endif; ?>
        <?php endif; ?>
    </div>
</body>
</html>
