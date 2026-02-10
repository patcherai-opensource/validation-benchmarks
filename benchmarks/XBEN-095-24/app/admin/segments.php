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
    <title>Segments - Customer Management Framework</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
        .header { background: #343a40; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; font-size: 20px; }
        .header .user-info { display: flex; align-items: center; gap: 15px; }
        .header a { color: #adb5bd; text-decoration: none; }
        .sidebar { width: 250px; background: #495057; position: fixed; height: 100%; padding-top: 20px; }
        .sidebar a { display: block; padding: 12px 20px; color: #adb5bd; text-decoration: none; border-left: 3px solid transparent; }
        .sidebar a:hover, .sidebar a.active { background: #343a40; color: white; border-left-color: #007bff; }
        .main { margin-left: 250px; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
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
        <a href="/admin/dashboard.php">Dashboard</a>
        <a href="/admin/customers.php">Customers</a>
        <a href="/admin/segments.php" class="active">Segments</a>
        <a href="/admin/segment-assignment.php">Segment Assignment</a>
        <a href="/admin/settings.php">Settings</a>
    </div>
    <div class="main">
        <div class="card">
            <h2>Segment Management</h2>
            <table>
                <thead><tr><th>ID</th><th>Name</th><th>Description</th><th>Members</th></tr></thead>
                <tbody>
                    <tr><td>1</td><td>Premium Users</td><td>High-value customers</td><td>234</td></tr>
                    <tr><td>2</td><td>Active Subscribers</td><td>Monthly active users</td><td>892</td></tr>
                    <tr><td>3</td><td>Trial Users</td><td>Currently in trial period</td><td>121</td></tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
