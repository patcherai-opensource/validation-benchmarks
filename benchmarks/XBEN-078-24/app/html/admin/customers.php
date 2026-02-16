<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();

$page = max(1, intval($_GET['page'] ?? 1));
$perPage = 25;
$offset = ($page - 1) * $perPage;

$total = $conn->query("SELECT COUNT(*) as cnt FROM objects WHERE o_type = 'object' AND o_className = 'Customer'")->fetch_assoc()['cnt'];
$stmt = $conn->prepare("SELECT * FROM objects WHERE o_type = 'object' AND o_className = 'Customer' ORDER BY o_id ASC LIMIT ? OFFSET ?");
$stmt->bind_param("ii", $perPage, $offset);
$stmt->execute();
$customers = $stmt->get_result();

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMF Admin - Customers</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-layout">
    <?php include __DIR__ . '/sidebar.php'; ?>
    <div class="admin-content">
        <div class="admin-header">
            <h1>Customer Objects</h1>
        </div>
        <div class="panel">
            <table class="data-table">
                <thead>
                    <tr><th>ID</th><th>Key</th><th>Class</th><th>Published</th><th>Parent ID</th></tr>
                </thead>
                <tbody>
                <?php while ($row = $customers->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo intval($row['o_id']); ?></td>
                        <td><?php echo htmlspecialchars($row['o_key']); ?></td>
                        <td><?php echo htmlspecialchars($row['o_className']); ?></td>
                        <td><?php echo $row['o_published'] ? 'Yes' : 'No'; ?></td>
                        <td><?php echo intval($row['o_parentId']); ?></td>
                    </tr>
                <?php endwhile; ?>
                </tbody>
            </table>
            <?php if ($total > $perPage): ?>
            <div class="pagination">
                <?php for ($i = 1; $i <= ceil($total / $perPage); $i++): ?>
                    <a href="?page=<?php echo $i; ?>" class="<?php echo $i === $page ? 'active' : ''; ?>"><?php echo $i; ?></a>
                <?php endfor; ?>
            </div>
            <?php endif; ?>
        </div>
    </div>
</div>
</body>
</html>