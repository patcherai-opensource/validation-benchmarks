<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: /login.php");
    exit();
}

$servername = getenv('MYSQL_HOST');
$db_username = getenv('MYSQL_USER');
$db_password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $db_username, $db_password, $dbname);

if ($conn->connect_error) {
    die("Service temporarily unavailable");
}

$username = htmlspecialchars($_SESSION['username']);
$role = htmlspecialchars($_SESSION['role']);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Segment Assignment - Customer Management Framework</title>
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
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        select, input[type="text"] { width: 300px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .results { margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .error { color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 4px; margin-bottom: 15px; }
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
        <a href="/admin/segment-assignment.php" class="active">Segment Assignment</a>
        <a href="/admin/settings.php">Settings</a>
    </div>
    <div class="main">
        <div class="card">
            <h2>Segment Assignment</h2>
            <p>Manage segment assignments for customers and objects. Use the form below to look up inheritable segments.</p>
            
            <form method="GET" action="/admin/inheritable-segments.php">
                <div class="form-group">
                    <label for="type">Entity Type:</label>
                    <select name="type" id="type">
                        <option value="customers">Customer</option>
                        <option value="objects">Object</option>
                        <option value="documents">Document</option>
                        <option value="assets">Asset</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="id">Entity ID:</label>
                    <input type="text" name="id" id="id" placeholder="Enter entity ID">
                </div>
                <button type="submit">Lookup Inheritable Segments</button>
            </form>
        </div>
        
        <div class="card">
            <h2>Recent Assignments</h2>
            <table>
                <thead>
                    <tr>
                        <th>Entity</th>
                        <th>Type</th>
                        <th>Segment</th>
                        <th>Assigned</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Customer #1247</td>
                        <td>customer</td>
                        <td>Premium Users</td>
                        <td>2024-01-15</td>
                    </tr>
                    <tr>
                        <td>Object #892</td>
                        <td>object</td>
                        <td>Active Subscribers</td>
                        <td>2024-01-14</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
<?php $conn->close(); ?>
