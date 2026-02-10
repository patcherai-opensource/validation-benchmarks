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

$id = isset($_REQUEST['id']) ? $_REQUEST['id'] : '';
$type = isset($_REQUEST['type']) ? $_REQUEST['type'] : '';

$result_data = null;
$error = null;

if ($id !== '' && $type !== '') {
    $parentIdColumn = ($type === 'object') ? 'o_parentId' : 'parentId';
    $idColumn = ($type === 'object') ? 'o_id' : 'id';
    
    $parentIdStatement = sprintf(
        "SELECT %s FROM %s WHERE %s = '%s'",
        $parentIdColumn,
        $type,
        $idColumn,
        $conn->real_escape_string($id)
    );
    
    $result = $conn->query($parentIdStatement);
    if ($result === false) {
        $error = "Query failed";
    } else {
        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $result_data = $row;
        } else {
            $error = "No records found for the specified entity";
        }
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Inheritable Segments - Customer Management Framework</title>
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
        .info { padding: 15px; background: #e9ecef; border-radius: 4px; margin-bottom: 15px; }
        .error { color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 4px; margin-bottom: 15px; }
        .success { padding: 15px; background: #d4edda; border-radius: 4px; color: #155724; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .back-link { margin-top: 20px; }
        .back-link a { color: #007bff; text-decoration: none; }
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
            <h2>Inheritable Segments Lookup</h2>
            
            <div class="info">
                <strong>Query Parameters:</strong><br>
                Type: <?php echo htmlspecialchars($type); ?><br>
                ID: <?php echo htmlspecialchars($id); ?>
            </div>
            
            <?php if ($error): ?>
                <div class="error"><?php echo htmlspecialchars($error); ?></div>
            <?php elseif ($result_data): ?>
                <div class="success">
                    <strong>Result:</strong>
                    <table>
                        <thead>
                            <tr>
                                <th>Field</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($result_data as $key => $value): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($key); ?></td>
                                <td><?php echo htmlspecialchars($value); ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php elseif ($id === '' || $type === ''): ?>
                <div class="info">Please provide both type and id parameters to perform a lookup.</div>
            <?php endif; ?>
            
            <div class="back-link">
                <a href="/admin/segment-assignment.php">&larr; Back to Segment Assignment</a>
            </div>
        </div>
    </div>
</body>
</html>
<?php $conn->close(); ?>
