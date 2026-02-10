<?php
session_start();
error_reporting(0);

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$isLoggedIn = isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;

if (!$isLoggedIn) {
    header("Location: admin.php");
    exit;
}

$subsiteContent = [];
$selectedSubsite = '';
$selectedTable = '';

$subsitesResult = $conn->query("SELECT id, name, table_name, description FROM subsites ORDER BY name");
$subsites = [];
while ($row = $subsitesResult->fetch_assoc()) {
    $subsites[] = $row;
}

if (isset($_GET['subsite'])) {
    $subsiteId = intval($_GET['subsite']);
    
    $subsiteQuery = $conn->query("SELECT name, table_name FROM subsites WHERE id = $subsiteId");
    if ($subsiteQuery && $row = $subsiteQuery->fetch_assoc()) {
        $selectedSubsite = $row['name'];
        $tableName = $row['table_name'];
        $selectedTable = $tableName;
        
        $contentQuery = "SELECT id, title, content, status, created_at FROM " . $tableName . " ORDER BY created_at DESC";
        $contentResult = $conn->query($contentQuery);
        
        if ($contentResult) {
            while ($content = $contentResult->fetch_assoc()) {
                $subsiteContent[] = $content;
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Subsites - Enterprise CMS</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Enterprise CMS - Subsite Management</h1>
    <nav>
        <a href="admin.php">Dashboard</a> |
        <a href="subsites.php">Manage Subsites</a> |
        <a href="admin.php?logout=1">Logout</a>
    </nav>
    <hr>
    
    <h2>Available Subsites</h2>
    <table border="1" cellpadding="8" cellspacing="0" style="width:100%; margin-bottom: 20px;">
        <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Actions</th>
        </tr>
        <?php foreach ($subsites as $site): ?>
        <tr>
            <td><?php echo htmlspecialchars($site['name']); ?></td>
            <td><?php echo htmlspecialchars($site['description']); ?></td>
            <td><a href="subsites.php?subsite=<?php echo $site['id']; ?>">View Content</a></td>
        </tr>
        <?php endforeach; ?>
    </table>
    
    <?php if ($selectedSubsite): ?>
    <h2>Content for: <?php echo htmlspecialchars($selectedSubsite); ?></h2>
    <?php if (count($subsiteContent) > 0): ?>
    <table border="1" cellpadding="8" cellspacing="0" style="width:100%;">
        <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Status</th>
            <th>Created</th>
        </tr>
        <?php foreach ($subsiteContent as $content): ?>
        <tr>
            <td><?php echo htmlspecialchars($content['id']); ?></td>
            <td><?php echo htmlspecialchars($content['title']); ?></td>
            <td><?php echo htmlspecialchars($content['status']); ?></td>
            <td><?php echo htmlspecialchars($content['created_at']); ?></td>
        </tr>
        <?php endforeach; ?>
    </table>
    <?php else: ?>
    <p>No content found for this subsite.</p>
    <?php endif; ?>
    <?php endif; ?>
</div>
</body>
</html>
<?php
$conn->close();
?>
