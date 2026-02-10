<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: /login.php");
    exit();
}

$username = htmlspecialchars($_SESSION['username']);
$role = htmlspecialchars($_SESSION['role']);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - Customer Management Framework</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
        .header { background: #343a40; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 20px; }
        .header .user-info { display: flex; align-items: center; gap: 15px; }
        .header a { color: #adb5bd; text-decoration: none; }
        .header a:hover { color: white; }
        .sidebar { width: 250px; background: #495057; position: fixed; height: 100%; padding-top: 20px; }
        .sidebar a { display: block; padding: 12px 20px; color: #adb5bd; text-decoration: none; border-left: 3px solid transparent; }
        .sidebar a:hover, .sidebar a.active { background: #343a40; color: white; border-left-color: #007bff; }
        .main { margin-left: 250px; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card .number { font-size: 36px; font-weight: bold; color: #007bff; }
        .stat-card .label { color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Customer Management Framework</h1>
        <div class="user-info">
            <span>Welcome, <?php echo $username; ?> (<?php echo $role; ?>)</span>
            <a href="/admin/logout.php">Logout</a>
        </div>
    </div>
    <div class="sidebar">
        <a href="/admin/dashboard.php" class="active">Dashboard</a>
        <a href="/admin/customers.php">Customers</a>
        <a href="/admin/segments.php">Segments</a>
        <a href="/admin/segment-assignment.php">Segment Assignment</a>
        <a href="/admin/settings.php">Settings</a>
    </div>
    <div class="main">
        <div class="stats">
            <div class="stat-card">
                <div class="number">1,247</div>
                <div class="label">Total Customers</div>
            </div>
            <div class="stat-card">
                <div class="number">23</div>
                <div class="label">Active Segments</div>
            </div>
            <div class="stat-card">
                <div class="number">892</div>
                <div class="label">Assignments</div>
            </div>
        </div>
        <div class="card">
            <h2>Recent Activity</h2>
            <p>No recent activity to display.</p>
        </div>
    </div>
</body>
</html>
