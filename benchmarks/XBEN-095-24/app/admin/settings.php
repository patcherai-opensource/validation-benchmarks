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
    <title>Settings - Customer Management Framework</title>
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
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        input[type="text"] { width: 300px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
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
        <a href="/admin/segments.php">Segments</a>
        <a href="/admin/segment-assignment.php">Segment Assignment</a>
        <a href="/admin/settings.php" class="active">Settings</a>
    </div>
    <div class="main">
        <div class="card">
            <h2>System Settings</h2>
            <form>
                <div class="form-group">
                    <label>Application Name:</label>
                    <input type="text" value="Customer Management Framework" disabled>
                </div>
                <div class="form-group">
                    <label>Version:</label>
                    <input type="text" value="3.3.9" disabled>
                </div>
                <div class="form-group">
                    <label>Database Status:</label>
                    <input type="text" value="Connected" disabled>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
