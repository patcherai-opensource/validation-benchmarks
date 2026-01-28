<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    $search = isset($_GET['q']) ? mysqli_real_escape_string($conn, $_GET['q']) : '';
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Members - SubSite Manager</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Member Management</h1>
    <p class="subtitle">Manage users and their permissions</p>
    
    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="subsites.php">SubSites</a>
        <a href="groups.php">Groups</a>
        <a href="members.php" class="active">Members</a>
        <a href="settings.php">Settings</a>
        <a href="cms-admin.php">CMS Admin</a>
    </nav>

    <div class="member-search">
        <form method="GET" action="members.php">
            <input type="text" name="q" placeholder="Search members..." value="<?php echo htmlspecialchars($search); ?>">
            <button type="submit">Search</button>
        </form>
    </div>

    <div class="member-list">
        <h2>All Members</h2>
        <?php
        $sql = "SELECT m.*, g.name as group_name FROM members m LEFT JOIN user_groups g ON m.group_id = g.id";
        if (!empty($search)) {
            $sql .= " WHERE m.email LIKE '%$search%' OR m.first_name LIKE '%$search%' OR m.last_name LIKE '%$search%'";
        }
        $sql .= " ORDER BY m.created_at DESC";
        
        $result = $conn->query($sql);
        if ($result && $result->num_rows > 0) {
            echo "<table class='data-table'>";
            echo "<tr><th>ID</th><th>Name</th><th>Email</th><th>Group</th><th>Status</th><th>Joined</th></tr>";
            while($row = $result->fetch_assoc()) {
                $name = htmlspecialchars($row['first_name'] . ' ' . $row['last_name']);
                $status = $row['is_active'] ? '<span class="status-active">Active</span>' : '<span class="status-inactive">Inactive</span>';
                echo "<tr>";
                echo "<td>{$row['id']}</td>";
                echo "<td>{$name}</td>";
                echo "<td>" . htmlspecialchars($row['email']) . "</td>";
                echo "<td>" . htmlspecialchars($row['group_name'] ?? 'None') . "</td>";
                echo "<td>{$status}</td>";
                echo "<td>{$row['created_at']}</td>";
                echo "</tr>";
            }
            echo "</table>";
        } else {
            echo "<p>No members found.</p>";
        }
        ?>
    </div>

    <div class="member-actions">
        <h3>Actions</h3>
        <ul>
            <li><a href="members.php?action=invite">Invite New Member</a></li>
            <li><a href="members.php?action=bulk">Bulk Import</a></li>
            <li><a href="members.php?action=export">Export Member List</a></li>
        </ul>
    </div>
</div>

<footer>
    <p>&copy; 2024 SubSite Manager v3.2.1</p>
</footer>
<?php $conn->close(); ?>
</body>
</html>
