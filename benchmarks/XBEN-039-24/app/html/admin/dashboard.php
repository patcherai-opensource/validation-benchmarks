<?php
session_start();

if (!isset($_SESSION['user_id'])) {
    header("Location: index.php");
    exit;
}

$conn = new mysqli(
    getenv('MYSQL_HOST') ?: 'localhost',
    getenv('MYSQL_USER') ?: 'user',
    getenv('MYSQL_PASSWORD') ?: 'password',
    getenv('MYSQL_DATABASE') ?: 'blogDB'
);

if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$action = isset($_GET['action']) ? $_GET['action'] : 'list';

$faq_count = 0;
$category_count = 0;
$result = $conn->query("SELECT COUNT(*) as cnt FROM faq_entries");
if ($result) {
    $faq_count = $result->fetch_assoc()['cnt'];
}
$result = $conn->query("SELECT COUNT(*) as cnt FROM faq_categories");
if ($result) {
    $category_count = $result->fetch_assoc()['cnt'];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - FAQ Admin</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
<div class="container admin-panel">
    <header class="admin-header">
        <h1>FAQ Administration</h1>
        <div class="user-info">
            Welcome, <?php echo htmlspecialchars($_SESSION['display_name']); ?> 
            (<?php echo htmlspecialchars($_SESSION['role']); ?>)
            | <a href="logout.php">Logout</a>
        </div>
    </header>
    
    <nav class="admin-nav">
        <a href="dashboard.php" <?php echo $action == 'list' ? 'class="active"' : ''; ?>>FAQ Entries</a>
        <a href="dashboard.php?action=insertentry" <?php echo $action == 'insertentry' ? 'class="active"' : ''; ?>>Add New Entry</a>
        <a href="categories.php">Categories</a>
        <a href="../index.php" target="_blank">View Site</a>
    </nav>
    
    <main class="admin-content">
        <?php if ($action == 'list'): ?>
            <h2>FAQ Entries</h2>
            <div class="stats">
                <p>Total Entries: <?php echo $faq_count; ?> | Categories: <?php echo $category_count; ?></p>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Question</th>
                        <th>Category</th>
                        <th>Author</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php
                    $sql = "SELECT e.*, c.name as category_name FROM faq_entries e 
                            LEFT JOIN faq_categories c ON e.category_id = c.id 
                            ORDER BY e.created_at DESC";
                    $result = $conn->query($sql);
                    if ($result && $result->num_rows > 0) {
                        while ($row = $result->fetch_assoc()) {
                            $status = $row['active'] ? 'Active' : 'Inactive';
                            $status_class = $row['active'] ? 'status-active' : 'status-inactive';
                            echo "<tr>
                                    <td>{$row['id']}</td>
                                    <td>" . htmlspecialchars(substr($row['question'], 0, 50)) . "...</td>
                                    <td>" . htmlspecialchars($row['category_name']) . "</td>
                                    <td>" . htmlspecialchars($row['author']) . "</td>
                                    <td><span class='{$status_class}'>{$status}</span></td>
                                    <td>
                                        <a href='dashboard.php?action=saveentry&id={$row['id']}'>Edit</a>
                                    </td>
                                  </tr>";
                        }
                    } else {
                        echo "<tr><td colspan='6'>No entries found.</td></tr>";
                    }
                    ?>
                </tbody>
            </table>
        <?php else: ?>
            <?php include 'faq_form.php'; ?>
        <?php endif; ?>
    </main>
</div>
</body>
</html>
<?php $conn->close(); ?>
