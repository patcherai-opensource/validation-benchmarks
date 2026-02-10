<?php
session_start();

// Check if user is logged in
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: login.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LibreNMS - Dashboard</title>
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
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
            color: #fff;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card .number {
            font-size: 36px;
            font-weight: 700;
            color: #e94560;
        }
        .stat-card .label {
            font-size: 14px;
            color: #aaa;
            margin-top: 5px;
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
        <a href="index.php" class="active">Dashboard</a>
        <a href="devices.php">Devices</a>
        
        <div class="section-title">Search</div>
        <a href="search.php?type=ipv4">IPv4 Address</a>
        <a href="search.php?type=ipv6">IPv6 Address</a>
        <a href="search.php?type=mac">MAC Address</a>
        <a href="search.php?type=arp">ARP Table</a>
        
        <div class="section-title">Reports</div>
        <a href="#">Alerts</a>
        <a href="#">Eventlog</a>
    </div>
    
    <main class="main-content">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="number">5</div>
                <div class="label">Total Devices</div>
            </div>
            <div class="stat-card">
                <div class="number">9</div>
                <div class="label">Ports</div>
            </div>
            <div class="stat-card">
                <div class="number">8</div>
                <div class="label">Ports Up</div>
            </div>
            <div class="stat-card">
                <div class="number">1</div>
                <div class="label">Ports Down</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Quick Navigation</h2>
            <p>Welcome to LibreNMS Network Management System. Use the sidebar to navigate through different sections.</p>
            <br>
            <p><strong>Search Functions:</strong></p>
            <ul style="margin-left: 20px; margin-top: 10px;">
                <li><a href="search.php?type=mac">MAC Address Search</a> - Find interfaces by MAC address</li>
                <li><a href="search.php?type=ipv4">IPv4 Search</a> - Search by IP address</li>
                <li><a href="devices.php">Device List</a> - View all monitored devices</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>System Information</h2>
            <p>User: <?php echo htmlspecialchars($_SESSION['username']); ?></p>
            <p>Access Level: <?php echo $_SESSION['level'] == 10 ? 'Administrator' : 'Operator'; ?></p>
        </div>
    </main>
</body>
</html>
